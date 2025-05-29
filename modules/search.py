"""Google Custom Search API integration."""

import json
from typing import Dict, List, Optional, TypedDict
import requests
from urllib.parse import urlparse

from utilities.env import CUSTOM_SEARCH_API_KEY, PROGRAMMABLE_SEARCH_ENGINE_ID

class SearchResult(TypedDict):
    """Typed dictionary for search result items."""
    title: str
    link: str
    snippet: str
    displayLink: str

class GoogleSearchError(Exception):
    """Exception raised for errors in the Google Search API."""
    pass

def google_search(query: str, num_results: int = 10) -> List[SearchResult]:
    """
    Perform a Google search using the Custom Search JSON API.
    
    Args:
        query: The search query string.
        num_results: Maximum number of results to return (max 10).
        
    Returns:
        A list of search result items.
        
    Raises:
        GoogleSearchError: If the API request fails or returns an error.
        ValueError: If required environment variables are missing.
    """
    if not CUSTOM_SEARCH_API_KEY or not PROGRAMMABLE_SEARCH_ENGINE_ID:
        raise ValueError("Missing required environment variables: CUSTOM_SEARCH_API_KEY and PROGRAMMABLE_SEARCH_ENGINE_ID must be set")
    
    if num_results > 10:
        num_results = 10  # Google Custom Search API max is 10 results per request
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': CUSTOM_SEARCH_API_KEY,
        'cx': PROGRAMMABLE_SEARCH_ENGINE_ID,
        'num': num_results
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'error' in data:
            error_msg = data['error'].get('message', 'Unknown error')
            raise GoogleSearchError(f"Google Search API error: {error_msg}")
            
        return data.get('items', [])
        
    except requests.exceptions.RequestException as e:
        raise GoogleSearchError(f"Failed to perform search: {str(e)}")
    except (json.JSONDecodeError, KeyError) as e:
        raise GoogleSearchError(f"Invalid response from Google Search API: {str(e)}")