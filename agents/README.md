# Datahouse Agents - Simple Tool System

A flexible, simple tool registration and execution system that uses semantic similarity for tool selection.

## How It Works

1. **Tool Examples**: Define examples in `TOOL_EXAMPLES` for semantic tool selection
2. **Tool Registry**: Register functions with parameter schemas for execution
3. **Automatic Selection**: ToolSelector uses embeddings to choose appropriate tools
4. **Simple Extraction**: Basic parameter extraction from user messages
5. **Generic Execution**: One execution engine for all tools

## Usage

### Basic Usage

```python
from agents.core import DatahouseAgent

# Initialize the agent
agent = DatahouseAgent()

# Process a query - automatically selects and executes tools
response = agent.process("search for latest news about AI")
print(response)
```

### Register Custom Tools

```python
# Define a function
def weather_function(city: str) -> str:
    return f"Weather in {city}: 22°C"

# Register the tool
agent.register_tool(
    name="get_weather",
    function=weather_function,
    parameter_schema={
        "city": {
            "type": str,
            "required": True,
            "description": "City name"
        }
    },
    description="Get weather information"
)
```

## Tool Configuration

### In tool_config.py

```python
TOOL_REGISTRY = {
    "google_search": {
        "function": google_search,
        "parameter_schema": {
            "query": {"type": str, "required": True},
            "num_results": {"type": int, "required": False, "default": 10}
        },
        "description": "Search the web"
    }
}

TOOL_EXAMPLES = [
    ("google_search", "search for latest news"),
    ("google_search", "find information about AI"),
    # ... more examples
]
```

## Key Benefits

- **Simple**: No complex extraction rules - examples handle selection
- **Flexible**: Easy to add new tools without modifying core code
- **Type Safe**: Automatic parameter validation
- **Generic**: One execution engine for all tools
- **Maintainable**: Configuration-driven approach

## Available Tools

- **google_search**: Web search using Google Custom Search API
- **get_page**: Retrieve and parse web page content

## Example Queries

- "search for latest news about AI" → Uses google_search
- "read https://example.com" → Uses get_page
- "hello, how are you?" → No tools (general conversation) 