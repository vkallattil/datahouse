import numpy as np
from openai import OpenAI
from typing import List, Tuple, Dict, Any, Optional
from .tool_config import TOOL_EXAMPLES, NEGATIVE_EXAMPLES
from .embedding_cache import EmbeddingCache

class ToolSelector:
    """
    A class for selecting tools based on semantic similarity between user queries and tool examples.
    Uses embeddings to match user intent to the most appropriate tool.
    """
    
    def __init__(self, client: OpenAI, cache_dir: str = "cache"):
        self.client = client
        self.tool_cache = EmbeddingCache(cache_dir, "tool")
        self.negative_cache = EmbeddingCache(cache_dir, "negative")
        self.embedding_store: Dict[str, List[float]] = {}
        self.negative_embeddings: Dict[str, List[float]] = {}
        
        # Pre-compute hashes once
        self.tool_data_hash = self.tool_cache._compute_hash(TOOL_EXAMPLES)
        self.negative_data_hash = self.negative_cache._compute_hash(NEGATIVE_EXAMPLES)
        
        # Try to load cached embeddings, build if not available
        if self._load_cached_embeddings():
            print("Loaded cached embeddings from disk")
        else:
            print("Building embeddings from scratch...")
            self._build_embeddings()
            self._build_negative_embeddings()
            self._save_cached_embeddings()
            print("Embeddings built and cached")
    
    def _save_cached_embeddings(self) -> bool:
        """Save embeddings to disk for future use. Returns True if successful."""
        # Save tool embeddings
        tool_success = self.tool_cache.save_embeddings(self.embedding_store, self.tool_data_hash)
        
        # Save negative embeddings
        negative_success = self.negative_cache.save_embeddings(self.negative_embeddings, self.negative_data_hash)
        
        return tool_success and negative_success
    
    def _load_cached_embeddings(self) -> bool:
        """Load embeddings from disk. Returns True if successful, False otherwise."""
        # Load tool embeddings
        tool_embeddings = self.tool_cache.load_embeddings(self.tool_data_hash)
        
        # Load negative embeddings
        negative_embeddings = self.negative_cache.load_embeddings(self.negative_data_hash)
        
        if tool_embeddings is not None and negative_embeddings is not None:
            self.embedding_store = tool_embeddings
            self.negative_embeddings = negative_embeddings
            return True
        
        return False
    
    def clear_cache(self) -> None:
        """Clear the cached embeddings and force rebuilding on next initialization."""
        self.tool_cache.clear_cache()
        self.negative_cache.clear_cache()
    
    def _build_embeddings(self) -> None:
        """Create and store embeddings for all tool examples."""
        try:
            for tool_name, example in TOOL_EXAMPLES:
                embedding = self.client.embeddings.create(
                    input=example,
                    model="text-embedding-3-small"
                )
                self.embedding_store[f"{tool_name}:{example}"] = embedding.data[0].embedding
        except Exception as e:
            print(f"Error building tool embeddings: {e}")
            raise
    
    def _build_negative_embeddings(self) -> None:
        """Create and store embeddings for all negative examples."""
        try:
            for example in NEGATIVE_EXAMPLES:
                embedding = self.client.embeddings.create(
                    input=example,
                    model="text-embedding-3-small"
                )
                self.negative_embeddings[example] = embedding.data[0].embedding
        except Exception as e:
            print(f"Error building negative embeddings: {e}")
            raise
    
    def _compute_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        try:
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float]) -> Tuple[Optional[str], float]:
        """
        Find the most similar stored embedding to the query embedding using cosine similarity.
        Returns a tuple of (most_similar_text, similarity_score)
        """
        max_similarity = -1
        most_similar_text = None
        
        for text, stored_embedding in self.embedding_store.items():
            similarity = self._compute_cosine_similarity(query_embedding, stored_embedding)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_text = text
                
        return most_similar_text, max_similarity
    
    def select_tool(self, message: str, threshold: float = 0.4, max_tools: int = 3) -> List[Tuple[str, float]]:
        """
        Select the most appropriate tools for a given user message.
        
        Args:
            message: The user's input message
            threshold: Minimum similarity score to consider a tool match
            max_tools: Maximum number of tools to return
            
        Returns:
            List of (tool_name, similarity_score) tuples, sorted by score descending.
            Returns empty list if no tools match or if query is too similar to negative examples.
        """
        try:
            # Embed user message
            message_embedding = self.client.embeddings.create(
                input=message,
                model="text-embedding-3-small"
            )
            
            query_embedding = message_embedding.data[0].embedding
            
            # First, check if this matches any negative examples (should NOT trigger tools)
            negative_score = self._get_negative_similarity(query_embedding)
            
            # If it's very similar to a negative example, don't trigger any tool
            if negative_score > 0.6:
                return []
            
            # Get all tool similarities above threshold
            tool_scores = self._get_all_tool_similarities(query_embedding, threshold)
            
            # Sort by score descending and return top max_tools
            sorted_tools = sorted(tool_scores, key=lambda x: x[1], reverse=True)
            return sorted_tools[:max_tools]
            
        except Exception as e:
            print(f"Error selecting tool for message: {e}")
            return []
    
    def _get_all_tool_similarities(self, query_embedding: List[float], threshold: float) -> List[Tuple[str, float]]:
        """
        Get all tools with similarity scores above the threshold.
        Returns a list of (tool_name, similarity_score) tuples.
        """
        tool_scores: Dict[str, float] = {}
        
        for text, stored_embedding in self.embedding_store.items():
            similarity = self._compute_cosine_similarity(query_embedding, stored_embedding)
            
            if similarity > threshold:
                tool_name = text.split(':')[0]
                # Keep the highest score for each tool
                if tool_name not in tool_scores or similarity > tool_scores[tool_name]:
                    tool_scores[tool_name] = similarity
        
        return list(tool_scores.items())
    
    def _get_negative_similarity(self, query_embedding: List[float]) -> float:
        """
        Get the highest similarity score with any negative example.
        """
        max_negative_similarity = -1
        
        for negative_example, stored_embedding in self.negative_embeddings.items():
            similarity = self._compute_cosine_similarity(query_embedding, stored_embedding)
            if similarity > max_negative_similarity:
                max_negative_similarity = similarity
                
        return max_negative_similarity
    
    def get_available_tools(self) -> List[str]:
        """Get a list of all available tool names."""
        return list(set(tool_name for tool_name, _ in TOOL_EXAMPLES))
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the cache status."""
        return {
            "tool_cache_size": self.tool_cache.get_cache_size(),
            "negative_cache_size": self.negative_cache.get_cache_size(),
            "tool_cache_valid": self.tool_cache.is_cache_valid(self.tool_data_hash),
            "negative_cache_valid": self.negative_cache.is_cache_valid(self.negative_data_hash),
            "embedding_count": len(self.embedding_store),
            "negative_count": len(self.negative_embeddings)
        } 