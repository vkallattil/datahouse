"""
Optimized ToolSelector - semantic tool selection using embeddings with simplified architecture.
"""

import numpy as np
from openai import OpenAI
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from .tool_config import TOOL_EXAMPLES, NEGATIVE_EXAMPLES
from .embedding_cache import EmbeddingCache

@dataclass
class EmbeddingData:
    """Container for embedding data."""
    embeddings: Dict[str, List[float]]
    data_hash: str

class UnifiedCacheManager:
    """Unified cache manager for both tool and negative embeddings."""
    
    def __init__(self, cache_dir: str):
        self.tool_cache = EmbeddingCache(cache_dir, "tool")
        self.negative_cache = EmbeddingCache(cache_dir, "negative")
    
    def save_all(self, tool_data: EmbeddingData, negative_data: EmbeddingData) -> bool:
        """Save both tool and negative embeddings."""
        tool_success = self.tool_cache.save_embeddings(tool_data.embeddings, tool_data.data_hash)
        negative_success = self.negative_cache.save_embeddings(negative_data.embeddings, negative_data.data_hash)
        return tool_success and negative_success
    
    def load_all(self, tool_hash: str, negative_hash: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Load both tool and negative embeddings."""
        tool_embeddings = self.tool_cache.load_embeddings(tool_hash)
        negative_embeddings = self.negative_cache.load_embeddings(negative_hash)
        return tool_embeddings, negative_embeddings
    
    def clear_all(self) -> None:
        """Clear all cached embeddings."""
        self.tool_cache.clear_cache()
        self.negative_cache.clear_cache()
    
    def get_info(self, tool_hash: str, negative_hash: str) -> Dict[str, Any]:
        """Get comprehensive cache information."""
        return {
            "tool_cache_size": self.tool_cache.get_cache_size(),
            "negative_cache_size": self.negative_cache.get_cache_size(),
            "tool_cache_valid": self.tool_cache.is_cache_valid(tool_hash),
            "negative_cache_valid": self.negative_cache.is_cache_valid(negative_hash)
        }

class ToolSelector:
    """Optimized tool selector with simplified architecture and better performance."""
    
    def __init__(self, client: OpenAI, cache_dir: str = "cache"):
        self.client = client
        self.cache_manager = UnifiedCacheManager(cache_dir)
        self.embedding_store: Dict[str, List[float]] = {}
        self.negative_embeddings: Dict[str, List[float]] = {}
        
        # Pre-compute hashes
        self.tool_hash = self.cache_manager.tool_cache._compute_hash(TOOL_EXAMPLES)
        self.negative_hash = self.cache_manager.negative_cache._compute_hash(NEGATIVE_EXAMPLES)
        
        # Initialize embeddings
        self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> None:
        """Initialize embeddings from cache or build new ones."""
        tool_embeddings, negative_embeddings = self.cache_manager.load_all(self.tool_hash, self.negative_hash)
        
        if tool_embeddings is not None and negative_embeddings is not None:
            self.embedding_store = tool_embeddings
            self.negative_embeddings = negative_embeddings
            print("Loaded cached embeddings from disk")
        else:
            print("Building embeddings from scratch...")
            self._build_all_embeddings()
            self._save_embeddings()
            print("Embeddings built and cached")
    
    def _build_all_embeddings(self) -> None:
        """Build all embeddings in a single operation."""
        try:
            # Build tool embeddings
            for tool_name, example in TOOL_EXAMPLES:
                embedding = self.client.embeddings.create(
                    input=example,
                    model="text-embedding-3-small"
                )
                self.embedding_store[f"{tool_name}:{example}"] = embedding.data[0].embedding
            
            # Build negative embeddings
            for example in NEGATIVE_EXAMPLES:
                embedding = self.client.embeddings.create(
                    input=example,
                    model="text-embedding-3-small"
                )
                self.negative_embeddings[example] = embedding.data[0].embedding
                
        except Exception as e:
            print(f"Error building embeddings: {e}")
            raise
    
    def _save_embeddings(self) -> None:
        """Save all embeddings to cache."""
        tool_data = EmbeddingData(self.embedding_store, self.tool_hash)
        negative_data = EmbeddingData(self.negative_embeddings, self.negative_hash)
        self.cache_manager.save_all(tool_data, negative_data)
    
    def _compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity using numpy for better performance."""
        try:
            v1, v2 = np.array(vec1), np.array(vec2)
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text with error handling."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def select_tool(self, message: str, threshold: float = 0.4, max_tools: int = 3) -> List[Tuple[str, float]]:
        """Select appropriate tools for user message."""
        try:
            query_embedding = self._get_embedding(message)
            if not query_embedding:
                return []
            
            # Check negative examples first
            if self._get_max_negative_similarity(query_embedding) > 0.6:
                return []
            
            # Get tool similarities
            tool_scores = self._get_tool_similarities(query_embedding, threshold)
            
            # Return top tools
            return sorted(tool_scores, key=lambda x: x[1], reverse=True)[:max_tools]
            
        except Exception as e:
            print(f"Error selecting tool: {e}")
            return []
    
    def _get_tool_similarities(self, query_embedding: List[float], threshold: float) -> List[Tuple[str, float]]:
        """Get tool similarities above threshold."""
        tool_scores: Dict[str, float] = {}
        
        for text, stored_embedding in self.embedding_store.items():
            similarity = self._compute_similarity(query_embedding, stored_embedding)
            
            if similarity > threshold:
                tool_name = text.split(':')[0]
                # Keep highest score for each tool
                if tool_name not in tool_scores or similarity > tool_scores[tool_name]:
                    tool_scores[tool_name] = similarity
        
        return list(tool_scores.items())
    
    def _get_max_negative_similarity(self, query_embedding: List[float]) -> float:
        """Get maximum similarity with negative examples."""
        if not self.negative_embeddings:
            return 0.0
        
        similarities = [
            self._compute_similarity(query_embedding, stored_embedding)
            for stored_embedding in self.negative_embeddings.values()
        ]
        return max(similarities) if similarities else 0.0
    
    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
        self.cache_manager.clear_all()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(set(tool_name for tool_name, _ in TOOL_EXAMPLES))
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive cache information."""
        cache_info = self.cache_manager.get_info(self.tool_hash, self.negative_hash)
        cache_info.update({
            "embedding_count": len(self.embedding_store),
            "negative_count": len(self.negative_embeddings)
        })
        return cache_info 