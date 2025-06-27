"""
Optimized configuration for tool registration and examples with reduced repetition.
"""

from typing import Dict, Any, Callable, List, Tuple
from modules.search import google_search
from modules.crawl import get_page

# Tool registration schema - more compact structure
TOOL_REGISTRY = {
    "google_search": {
        "function": google_search,
        "parameter_schema": {
            "query": {"type": str, "required": True, "description": "Search query string"},
            "num_results": {"type": int, "required": False, "default": 10, "description": "Number of results to return (max 10)"}
        },
        "description": "Search the web for current information"
    },
    "get_page": {
        "function": get_page,
        "parameter_schema": {
            "url": {"type": str, "required": True, "description": "URL of the page to retrieve"}
        },
        "description": "Retrieve and parse content from web pages"
    }
}

# Tool examples - more compact format
TOOL_EXAMPLES = [
    # Google Search examples
    ("google_search", "find the latest news about iran"),
    ("google_search", "search for current information"),
    ("google_search", "get the latest report"),
    ("google_search", "look up recent updates"),
    ("google_search", "find current facts"),
    ("google_search", "search for latest news"),
    ("google_search", "get up to date information"),
    ("google_search", "find recent reports"),
    ("google_search", "search the web for current events"),
    ("google_search", "look up latest statistics"),
    ("google_search", "search the web"),
    ("google_search", "find information online"),
    ("google_search", "get current data"),
    ("google_search", "look up facts online"),
    ("google_search", "search for information"),
    
    # Get Page examples
    ("get_page", "read this webpage"),
    ("get_page", "extract content from url"),
    ("get_page", "analyze this article"),
    ("get_page", "read the content of this page"),
    ("get_page", "extract text from website"),
    ("get_page", "get content from this url"),
    ("get_page", "read and summarize this page"),
    ("get_page", "analyze webpage content"),
    ("get_page", "read this article"),
    ("get_page", "extract from this page"),
    ("get_page", "get content from webpage"),
    ("get_page", "read webpage content"),
]

# Negative examples - categorized for better organization
NEGATIVE_EXAMPLES = [
    # General conversation
    "hello", "hi", "how are you", "goodbye", "bye", "thank you", "thanks",
    
    # AI questions
    "what is your name", "what can you do", "help", "who are you",
    "tell me about yourself", "what are your capabilities",
    
    # General knowledge (no tools needed)
    "what is the capital of france", "how many planets are in the solar system",
    "what is the meaning of life", "explain photosynthesis",
    "what is machine learning", "how does gravity work",
    "what is the difference between a cat and a dog",
    
    # Creative requests
    "tell me a joke", "write a poem", "create a story",
    "give me advice", "what should I do", "recommend something",
    
    # Simple calculations/definitions
    "what is 2+2", "define happiness", "explain democracy",
    "what does this word mean", "calculate something",
    
    # Opinions/preferences
    "what do you think about", "do you like", "what's your opinion",
    "which is better", "should I",
    
    # Meta questions
    "what did you just say", "repeat that", "can you explain",
    "I don't understand", "what do you mean",
    
    # Clarifications
    "what", "huh", "pardon", "excuse me",
    
    # General information (not current)
    "what is a computer", "how do plants grow", "what is love",
    "explain quantum physics", "what is the internet",
] 