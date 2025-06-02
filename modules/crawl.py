import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from utilities.logger import logger
import urllib.parse

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