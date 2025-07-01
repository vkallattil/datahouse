"""
Unified Tool Registry - combines tool selection, registration, validation, and execution.
"""

import numpy as np
from openai import OpenAI
from typing import Dict, Any, Callable, List, Tuple, Optional
from dataclasses import dataclass
from .tool_config import TOOL_REGISTRY, TOOL_EXAMPLES, NEGATIVE_EXAMPLES
from .embedding_cache import EmbeddingCache
from .parameter_extractor import LLMParameterExtractor
from utilities.agent_utils import validate_and_convert_parameters, extract_parameters_simple

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

class ToolRegistry:
    """Unified tool registry with semantic selection, registration, validation, and execution."""
    
    def __init__(self, client: OpenAI = None, cache_dir: str = "cache"):
        self.client = client
        self.tools = TOOL_REGISTRY.copy()
        self.parameter_extractor = LLMParameterExtractor(client) if client else None
        
        # Initialize embedding-based tool selection if client is available
        if client:
            self.cache_manager = UnifiedCacheManager(cache_dir)
            self.embedding_store: Dict[str, List[float]] = {}
            self.negative_embeddings: Dict[str, List[float]] = {}
            
            # Pre-compute hashes
            self.tool_hash = self.cache_manager.tool_cache._compute_hash(TOOL_EXAMPLES)
            self.negative_hash = self.cache_manager.negative_cache._compute_hash(NEGATIVE_EXAMPLES)
            
            # Initialize embeddings
            self._initialize_embeddings()
        else:
            self.cache_manager = None
            self.embedding_store = {}
            self.negative_embeddings = {}
    
    def _initialize_embeddings(self) -> None:
        """Initialize embeddings from cache or build new ones."""
        if not self.client:
            return
            
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
        if not self.client:
            return
            
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
        if not self.client or not self.cache_manager:
            return
            
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
        if not self.client:
            return []
            
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
        """Select appropriate tools for user message using semantic similarity."""
        if not self.client:
            return []
            
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
    
    def register_tool(self, name: str, function: Callable, parameter_schema: Dict[str, Any], description: str = "") -> None:
        """Register a new tool with the registry."""
        self.tools[name] = {
            "function": function,
            "parameter_schema": parameter_schema,
            "description": description
        }
    
    def unregister_tool(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self.tools:
            del self.tools[name]
            return True
        return False
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool configuration by name."""
        return self.tools.get(name)
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tool names."""
        return list(self.tools.keys())
    
    def extract_parameters(self, message: str, tool_name: str) -> Dict[str, Any]:
        """Extract parameters for a tool from a user message."""
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return {}
        
        parameter_schema = tool_config.get("parameter_schema", {})
        
        # Use LLM-based extraction if available
        if self.parameter_extractor:
            try:
                return self.parameter_extractor.extract_parameters(
                    message, tool_name, parameter_schema
                )
            except Exception as e:
                print(f"LLM extraction failed, falling back to simple extraction: {e}")
        
        # Fallback to simple extraction using utility function
        return extract_parameters_simple(message, tool_name, parameter_schema)
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Validate parameters against the tool's schema (legacy interface)."""
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return False, {}, ["Tool not found"]
        
        schema = tool_config.get("parameter_schema", {})
        result = validate_and_convert_parameters(parameters, schema)
        return result.is_valid, result.validated_params, result.errors
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """Execute a tool with the given parameters."""
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return False, None, f"Tool '{tool_name}' not found"
        
        # Validate parameters
        is_valid, validated_params, errors = self.validate_parameters(tool_name, parameters)
        if not is_valid:
            return False, None, f"Parameter validation failed: {', '.join(errors)}"
        
        try:
            # Execute the tool
            function = tool_config["function"]
            result = function(**validated_params)
            return True, result, ""
        except Exception as e:
            return False, None, f"Tool execution failed: {str(e)}"
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about all registered tools."""
        info = {}
        for name, config in self.tools.items():
            info[name] = {
                "description": config.get("description", ""),
                "parameters": list(config.get("parameter_schema", {}).keys()),
                "required_parameters": [
                    param for param, schema in config.get("parameter_schema", {}).items()
                    if schema.get("required", False)
                ]
            }
        return info
    
    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
        if self.cache_manager:
            self.cache_manager.clear_all()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive cache information."""
        if not self.cache_manager:
            return {
                "embedding_count": 0,
                "negative_count": 0,
                "tool_cache_size": 0,
                "negative_cache_size": 0,
                "tool_cache_valid": False,
                "negative_cache_valid": False
            }
        
        cache_info = self.cache_manager.get_info(self.tool_hash, self.negative_hash)
        cache_info.update({
            "embedding_count": len(self.embedding_store),
            "negative_count": len(self.negative_embeddings)
        })
        return cache_info 