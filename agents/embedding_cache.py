"""
Optimized embedding cache module with simplified file operations and better performance.
"""

import json
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

class EmbeddingCache:
    """Optimized cache system for storing and retrieving embeddings."""
    
    def __init__(self, cache_dir: str = "cache", prefix: str = "tool"):
        self.cache_dir = Path(cache_dir)
        self.prefix = prefix
        self.cache_dir.mkdir(exist_ok=True)
    
    def _compute_hash(self, data: Any) -> str:
        """Compute deterministic hash for data."""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def _get_cache_files(self) -> tuple[Path, Path]:
        """Get cache file paths."""
        embeddings_file = self.cache_dir / f"{self.prefix}_embeddings.pkl"
        metadata_file = self.cache_dir / f"{self.prefix}_metadata.json"
        return embeddings_file, metadata_file
    
    def save_embeddings(self, embeddings: Dict[str, Any], data_hash: str, version: str = "1.0") -> bool:
        """Save embeddings to disk with metadata."""
        try:
            embeddings_file, metadata_file = self._get_cache_files()
            
            # Save embeddings
            with embeddings_file.open('wb') as f:
                pickle.dump(embeddings, f)
            
            # Save metadata
            metadata = {
                "data_hash": data_hash,
                "version": version,
                "prefix": self.prefix
            }
            with metadata_file.open('w') as f:
                json.dump(metadata, f)
            
            return True
        except Exception as e:
            print(f"Error saving embeddings for {self.prefix}: {e}")
            return False
    
    def load_embeddings(self, current_data_hash: str) -> Optional[Dict[str, Any]]:
        """Load embeddings from disk if cache is valid."""
        embeddings_file, metadata_file = self._get_cache_files()
        
        # Check if cache files exist
        if not (embeddings_file.exists() and metadata_file.exists()):
            return None
        
        try:
            # Load and validate metadata
            with metadata_file.open('r') as f:
                metadata = json.load(f)
            
            # Check if cache is still valid
            if metadata.get("data_hash") != current_data_hash:
                print(f"Cache invalid for {self.prefix} - data has changed")
                return None
            
            # Load embeddings
            with embeddings_file.open('rb') as f:
                embeddings = pickle.load(f)
            
            return embeddings
            
        except Exception as e:
            print(f"Error loading cached embeddings for {self.prefix}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear the cached embeddings for this prefix."""
        embeddings_file, metadata_file = self._get_cache_files()
        
        for file_path in [embeddings_file, metadata_file]:
            if file_path.exists():
                file_path.unlink()
                print(f"Removed cache file: {file_path}")
    
    def get_cache_info(self) -> Optional[Dict[str, Any]]:
        """Get cache metadata if exists."""
        _, metadata_file = self._get_cache_files()
        
        if not metadata_file.exists():
            return None
        
        try:
            with metadata_file.open('r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def is_cache_valid(self, current_data_hash: str) -> bool:
        """Check if cache is valid for the given data hash."""
        cache_info = self.get_cache_info()
        if not cache_info:
            return False
        
        return cache_info.get("data_hash") == current_data_hash
    
    def get_cache_size(self) -> int:
        """Get the size of cached embeddings in bytes."""
        embeddings_file, _ = self._get_cache_files()
        
        if embeddings_file.exists():
            return embeddings_file.stat().st_size
        return 0 