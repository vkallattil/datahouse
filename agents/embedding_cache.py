"""
Embedding cache module for persisting and loading embeddings from disk.
Handles cache validation, storage, and retrieval with automatic invalidation.
"""

import json
import os
import pickle
import hashlib
from typing import Dict, Any, Tuple, Optional
from openai import OpenAI

class EmbeddingCache:
    """
    A cache system for storing and retrieving embeddings with automatic invalidation.
    """
    
    def __init__(self, cache_dir: str = "cache", prefix: str = "tool"):
        self.cache_dir = cache_dir
        self.prefix = prefix
        os.makedirs(cache_dir, exist_ok=True)
    
    def _compute_hash(self, data: Any) -> str:
        """Compute a deterministic hash for the given data."""
        # Convert to a consistent string representation
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        # Use SHA-256 for a deterministic hash
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def _get_cache_files(self) -> Tuple[str, str]:
        """Get the file paths for cached embeddings."""
        embeddings_file = os.path.join(self.cache_dir, f"{self.prefix}_embeddings.pkl")
        metadata_file = os.path.join(self.cache_dir, f"{self.prefix}_metadata.json")
        return embeddings_file, metadata_file
    
    def save_embeddings(self, 
                       embeddings: Dict[str, Any], 
                       data_hash: str, 
                       version: str = "1.0") -> bool:
        """
        Save embeddings to disk with metadata for cache validation.
        
        Args:
            embeddings: The embeddings to save
            data_hash: Hash of the data used to generate embeddings
            version: Version string for cache metadata
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            embeddings_file, metadata_file = self._get_cache_files()
            
            # Save embeddings
            with open(embeddings_file, 'wb') as f:
                pickle.dump(embeddings, f)
            
            # Save metadata
            metadata = {
                "data_hash": data_hash,
                "version": version,
                "prefix": self.prefix
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
            
            return True
        except Exception as e:
            print(f"Error saving embeddings for {self.prefix}: {e}")
            return False
    
    def load_embeddings(self, current_data_hash: str) -> Optional[Dict[str, Any]]:
        """
        Load embeddings from disk if cache is valid.
        
        Args:
            current_data_hash: Hash of current data to validate cache
            
        Returns:
            Loaded embeddings if cache is valid, None otherwise
        """
        embeddings_file, metadata_file = self._get_cache_files()
        
        # Check if cache files exist
        if not all(os.path.exists(f) for f in [embeddings_file, metadata_file]):
            return None
        
        try:
            # Load and validate metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check if cache is still valid
            if metadata.get("data_hash") != current_data_hash:
                print(f"Cache invalid for {self.prefix} - data has changed")
                return None
            
            # Load embeddings
            with open(embeddings_file, 'rb') as f:
                embeddings = pickle.load(f)
            
            return embeddings
            
        except Exception as e:
            print(f"Error loading cached embeddings for {self.prefix}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear the cached embeddings for this prefix."""
        embeddings_file, metadata_file = self._get_cache_files()
        
        for file_path in [embeddings_file, metadata_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed cache file: {file_path}")
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the cache for this prefix.
        
        Returns:
            Cache metadata if exists, None otherwise
        """
        _, metadata_file = self._get_cache_files()
        
        if not os.path.exists(metadata_file):
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def is_cache_valid(self, current_data_hash: str) -> bool:
        """
        Check if cache is valid for the given data hash.
        
        Args:
            current_data_hash: Hash of current data
            
        Returns:
            True if cache is valid, False otherwise
        """
        cache_info = self.get_cache_info()
        if not cache_info:
            return False
        
        return cache_info.get("data_hash") == current_data_hash
    
    def get_cache_size(self) -> int:
        """
        Get the size of cached embeddings in bytes.
        
        Returns:
            Size in bytes, 0 if no cache exists
        """
        embeddings_file, _ = self._get_cache_files()
        
        if os.path.exists(embeddings_file):
            return os.path.getsize(embeddings_file)
        return 0 