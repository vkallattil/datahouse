import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from utilities.logger import logger
import urllib.parse
from utilities.logger import logger
from utilities.config import CUSTOM_SEARCH_API_KEY, PROGRAMMABLE_SEARCH_ENGINE_ID

def crawl_links(start_url, max_depth):
    """
    Recursively crawl links starting from the `start_url` up to `max_depth`. 
    
    Parameters:
        start_url (str): The initial URL to crawl from.
        max_depth (int): The maximum depth to crawl.
    
    Returns:
        dict: A dictionary mapping each visited URL to a list of outbound links found on that page.
    """
    visited = set()   # To track visited URLs and avoid loops
    link_map = {}     # To store the mapping: page URL -> list of discovered links

    def crawl(current_url, depth):
        # Base case: Do not traverse beyond the desired depth
        if depth > max_depth:
            return
        
        # Avoid revisiting the same URL twice
        if current_url in visited:
            return
        
        visited.add(current_url)
        
        soup = get_page(current_url)
        if not soup:
            return

        links = set()

        for tag in soup.find_all('a', href=True):
            absolute = urllib.parse.urljoin(current_url, tag['href'])
            links.add(absolute)

        link_map[current_url] = list(links)

        for link in links:
            crawl(link, depth + 1)

    # Start the crawling process with the initial URL and depth 0
    crawl(start_url, 0)
    return link_map

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

def extract_text_from_page(page: BeautifulSoup) -> str:
    """
    Get raw text from a page.

    Args:
        page (BeautifulSoup): Parsed HTML content

    Returns:
        str: Cleaned and extracted text content
    """
    for script in page(['script', 'style']):
        script.decompose()

    content = page.find_all(['article', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
    clean_text = [element.get_text(strip=True) for element in content if element.get_text(strip=True)]
    return "\n\n".join(clean_text)
    
def get_search_results(query: str) -> Optional[Dict]:
    """
    Perform a search query using Google Custom Search API.
    
    Args:
        query (str): Search query string
        
    Returns:
        Optional[Dict]: JSON response from the API or None if error occurs
    """
    try:
        url = (f"https://www.googleapis.com/customsearch/v1"
               f"?key={CUSTOM_SEARCH_API_KEY}"
               f"&cx={PROGRAMMABLE_SEARCH_ENGINE_ID}"
               f"&q={query}")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        return response.json()["items"]
    
    except requests.RequestException as e:
        logger.error(f"Error making search request: {e}")
        
        return None

def get_pages_from_search_results(results: List[Dict]) -> List[Dict]:
    """
    Get and parse pages for each URL in a list of search results.

    Args:
        results (List[Dict]): List of search result items

    Returns:
        List[Dict]: List of search result data with attached page content
    """
    pages = []

    for i, result in enumerate(results):
        logger.info(f"Crawling result {i+1}/{len(results)}: {result['link']}")
        page = get_page(result["link"])
        
        if page is None:
            pages.append({
                "link": result["link"],
                "content": None,
                "error": "HTTP or parsing error"
            })
            continue
        
        pages.append({
            "link": result["link"],
            "content": page,
            "error": None
        })

    successful = sum(1 for page in pages if page.get("content") is not None)
    logger.info(f"Crawled {successful}/{len(pages)} pages successfully")

    return pages

