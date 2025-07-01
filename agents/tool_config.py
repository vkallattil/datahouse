"""
Optimized configuration for tool registration and examples with reduced repetition.
"""

from typing import Dict, Any, Callable, List, Tuple
from modules.search import search_and_read

# Tool registration schema - more compact structure
TOOL_REGISTRY = {
    "search_and_read": {
        "function": search_and_read,
        "parameter_schema": {
            "query": {"type": str, "required": True, "description": "Search query string"}
        },
        "description": "Search the web and retrieve main content from the top 5 results."
    }
}

# Tool examples - more compact format
TOOL_EXAMPLES = [
    ("search_and_read", "find the latest news about Iran"),
    ("search_and_read", "search for current information on AI safety"),
    ("search_and_read", "get the latest report on climate change"),
    ("search_and_read", "look up recent updates in quantum computing"),
    ("search_and_read", "find current facts about electric vehicles"),
    ("search_and_read", "search for latest news on Mars missions"),
    ("search_and_read", "get up to date information on COVID-19 vaccines"),
    ("search_and_read", "find recent reports on inflation rates"),
    ("search_and_read", "search the web for current events in technology"),
    ("search_and_read", "look up latest statistics on renewable energy"),
    ("search_and_read", "find information online about Python 3.12"),
    ("search_and_read", "get current data on global temperatures"),
    ("search_and_read", "look up facts online about the James Webb telescope"),
    ("search_and_read", "search for information on new battery technologies"),
    ("search_and_read", "find the most recent research on Alzheimer's disease"),
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