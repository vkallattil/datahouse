"""Google Custom Search API integration."""

import json
from typing import Dict, List, Optional, TypedDict
from pathlib import Path
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from utilities.env import CUSTOM_SEARCH_API_KEY, PROGRAMMABLE_SEARCH_ENGINE_ID
from utilities.logger import logger
from utilities.tool_decorator import tool

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

        items = data.get('items', [])
            
        return items
        
    except requests.exceptions.RequestException as e:
        raise GoogleSearchError(f"Failed to perform search: {str(e)}")
    except (json.JSONDecodeError, KeyError) as e:
        raise GoogleSearchError(f"Invalid response from Google Search API: {str(e)}")

def get_page(url: str) -> BeautifulSoup:
    """
    Get a page at a URL.
    Args:
        url (str): URL of the page to crawl
    Returns:
        BeautifulSoup: Parsed HTML content
    Raises:
        Exception: If any error occurs during crawling
    """
    try:
        headers = {
            "User-Agent": "SimpleCrawler/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info(f"Crawled page {url}")
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logger.error(f"Error crawling page {url}: {e}")
        return None

def extract_main_text(soup):
    """Extract main text content from a BeautifulSoup object."""
    if soup is None:
        return ""
    # Remove script and style elements
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    # Try to find main/article tag, else fallback to body
    main = soup.find('main') or soup.find('article') or soup.body
    if not main:
        return ""
    text = main.get_text(separator=' ', strip=True)
    # Collapse whitespace
    return ' '.join(text.split())

@tool
def search_and_read(query: str) -> List[Dict[str, str]]:
    """
    Perform a Google search and retrieve main content from the top 5 results.
    Args:
        query: The search query string.
    Returns:
        List of dicts: [{"url": ..., "content": ...}, ...]
    """
    results = google_search(query, num_results=5)
    output = []
    for item in results:
        url = item.get('link')
        soup = get_page(url)
        content = extract_main_text(soup)
        output.append({"url": url, "content": content})
    return output