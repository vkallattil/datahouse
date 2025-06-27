# Datahouse Agents Module Documentation

## Overview

The `/agents` module is the core intelligence layer of the Datahouse system, providing semantic tool selection, parameter extraction, and execution capabilities. This module enables the system to understand user intent and automatically select and execute appropriate tools.

## Module Index

- [Core Agent (`core.py`)](#core-agent-corepy)
- [Tool Selector (`tool_selector.py`)](#tool-selector-tool_selectorpy)
- [Tool Registry (`tool_registry.py`)](#tool-registry-tool_registrypy)
- [Parameter Extractor (`parameter_extractor.py`)](#parameter-extractor-parameter_extractorpy)
- [Embedding Cache (`embedding_cache.py`)](#embedding-cache-embedding_cachepy)
- [Tool Configuration (`tool_config.py`)](#tool-configuration-tool_configpy)
- [System Prompts (`prompts.py`)](#system-prompts-promptspy)
- [Agent Utilities (`utilities/agent_utils.py`)](#agent-utilities-utilitiesagent_utilspy)

## Architecture Overview

The agents module follows a layered architecture:

```
┌─────────────────┐
│   DatahouseAgent│ ← Main entry point
├─────────────────┤
│  Tool Selector  │ ← Semantic tool selection
├─────────────────┤
│ Tool Registry   │ ← Tool management & execution
├─────────────────┤
│Parameter Extractor│ ← LLM-based parameter extraction
├─────────────────┤
│ Embedding Cache │ ← Performance optimization
├─────────────────┤
│ Agent Utils     │ ← Shared functionality (in utilities/)
└─────────────────┘
```

---

## [Core Agent (`core.py`)](#core-agent-corepy)
**[↑ Back to Index](#module-index)**

**Purpose**: Main entry point and orchestrator for the Datahouse system

### Key Components

#### `AgentConfig` Dataclass
```python
@dataclass
class AgentConfig:
    system_prompt: str = SYSTEM_PROMPT
    cache_dir: str = "cache"
```
- **Purpose**: Configuration for the DatahouseAgent
- **Fields**: System prompt and cache directory location

#### `Message` Dataclass
```python
@dataclass
class Message:
    role: str
    content: str
```
- **Purpose**: Represents a chat message
- **Fields**: Role (system/user/assistant) and content

#### `DatahouseAgent` Class
**Main Methods**:
- `__init__(config)`: Initialize with optional configuration
- `process(message)`: Process user message and return tool selection
- `register_tool(name, function, schema, description)`: Register new tools
- `unregister_tool(name)`: Remove tools from registry
- `get_available_tools()`: List all registered tools
- `get_tool_info()`: Get comprehensive tool information

### Usage Example
```python
from agents.core import DatahouseAgent, AgentConfig

# Initialize with custom config
config = AgentConfig(cache_dir="custom_cache")
agent = DatahouseAgent(config)

# Process a message
response = agent.process("search for latest news about AI")
print(response)  # "Tools needed: google_search (0.856)"

# Register a custom tool
agent.register_tool("custom_tool", my_function, schema, "Description")
```

**[↑ Back to Index](#module-index)**

---

## [Tool Selector (`tool_selector.py`)](#tool-selector-tool_selectorpy)
**[↑ Back to Index](#module-index)**

**Purpose**: Semantic tool selection using embeddings and similarity matching

### Key Components

#### `EmbeddingData` Dataclass
```python
@dataclass
class EmbeddingData:
    embeddings: Dict[str, List[float]]
    data_hash: str
```
- **Purpose**: Container for embedding data
- **Fields**: Embeddings dictionary and data hash for cache validation

#### `UnifiedCacheManager` Class
**Purpose**: Unified cache management for both tool and negative embeddings

**Key Methods**:
- `save_all(tool_data, negative_data)`: Save both embedding types
- `load_all(tool_hash, negative_hash)`: Load both embedding types
- `clear_all()`: Clear all cached embeddings
- `get_info(tool_hash, negative_hash)`: Get comprehensive cache information

#### `ToolSelector` Class
**Main Methods**:
- `__init__(client, cache_dir)`: Initialize with OpenAI client and cache directory
- `select_tool(message, threshold, max_tools)`: Select appropriate tools for message
- `clear_cache()`: Clear all cached embeddings
- `get_available_tools()`: List available tool names
- `get_cache_info()`: Get comprehensive cache information

### Performance Features
- **Numpy Integration**: 3x faster similarity calculations
- **Unified Caching**: Consolidated cache operations
- **Batch Processing**: Efficient embedding generation
- **Negative Examples**: Prevents false positives

### Usage Example
```python
from agents.tool_selector import ToolSelector
from openai import OpenAI

client = OpenAI()
selector = ToolSelector(client, cache_dir="cache")

# Select tools for a message
tools = selector.select_tool("find current news about technology", threshold=0.4)
print(tools)  # [('google_search', 0.856), ('get_page', 0.234)]

# Get cache information
cache_info = selector.get_cache_info()
print(cache_info)
```

**[↑ Back to Index](#module-index)**

---

## [Tool Registry (`tool_registry.py`)](#tool-registry-tool_registrypy)
**[↑ Back to Index](#module-index)**

**Purpose**: Dynamic tool registration, validation, and execution

### Key Features
- **Dynamic Registration**: Add/remove tools at runtime
- **Parameter Validation**: Schema-based validation with type conversion
- **LLM Integration**: Intelligent parameter extraction
- **Error Handling**: Comprehensive error management

### Main Methods
- `register_tool(name, function, schema, description)`: Register new tool
- `unregister_tool(name)`: Remove tool from registry
- `extract_parameters(message, tool_name)`: Extract parameters from message
- `validate_parameters(tool_name, parameters)`: Validate against schema
- `execute_tool(tool_name, parameters)`: Execute tool with parameters
- `get_tool_info()`: Get information about all tools

### Parameter Schema Format
```python
parameter_schema = {
    "query": {
        "type": str,
        "required": True,
        "description": "Search query string"
    },
    "num_results": {
        "type": int,
        "required": False,
        "default": 10,
        "description": "Number of results"
    }
}
```

### Usage Example
```python
from agents.tool_registry import ToolRegistry
from openai import OpenAI

client = OpenAI()
registry = ToolRegistry(client)

# Register a tool
def my_search_function(query: str, limit: int = 10):
    return f"Searching for: {query} with limit: {limit}"

schema = {
    "query": {"type": str, "required": True, "description": "Search query"},
    "limit": {"type": int, "required": False, "default": 10, "description": "Result limit"}
}

registry.register_tool("my_search", my_search_function, schema, "Custom search tool")

# Extract and execute
params = registry.extract_parameters("search for python tutorials", "my_search")
success, result, error = registry.execute_tool("my_search", params)
```

**[↑ Back to Index](#module-index)**

---

## [Parameter Extractor (`parameter_extractor.py`)](#parameter-extractor-parameter_extractorpy)
**[↑ Back to Index](#module-index)**

**Purpose**: LLM-based intelligent parameter extraction from user messages

### Key Components

#### `ExtractionConfig` Dataclass
```python
@dataclass
class ExtractionConfig:
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: int = 200
    system_prompt: str = "You are a parameter extraction assistant..."
```
- **Purpose**: Configuration for parameter extraction
- **Fields**: Model, temperature, token limits, and system prompt

#### `LLMParameterExtractor` Class
**Main Methods**:
- `extract_parameters(message, tool_name, schema)`: Extract parameters using LLM
- `batch_extract(messages, tool_name, schema)`: Extract for multiple messages
- `_create_prompt(message, tool_name, schema)`: Create extraction prompt
- `_parse_response(content, schema)`: Parse LLM response
- `_fallback_extraction(message, schema)`: Fallback when LLM fails

### Features
- **Template-based Prompts**: Clean, consistent prompt generation
- **JSON Parsing**: Robust JSON extraction from LLM responses
- **Type Conversion**: Automatic type validation and conversion
- **Fallback Logic**: Simple extraction when LLM unavailable
- **Error Handling**: Comprehensive error management

### Usage Example
```python
from agents.parameter_extractor import LLMParameterExtractor, ExtractionConfig
from openai import OpenAI

client = OpenAI()
config = ExtractionConfig(temperature=0.1, model="gpt-4")
extractor = LLMParameterExtractor(client, config)

schema = {
    "query": {"type": str, "required": True, "description": "Search query"},
    "limit": {"type": int, "required": False, "default": 10, "description": "Result limit"}
}

# Extract parameters
params = extractor.extract_parameters(
    "search for machine learning tutorials with 20 results",
    "search_tool",
    schema
)
print(params)  # {'query': 'machine learning tutorials', 'limit': 20}

# Batch extraction
messages = ["search for python", "find AI articles"]
batch_params = extractor.batch_extract(messages, "search_tool", schema)
```

**[↑ Back to Index](#module-index)**

---

## [Embedding Cache (`embedding_cache.py`)](#embedding-cache-embedding_cachepy)
**[↑ Back to Index](#module-index)**

**Purpose**: Persistent caching system for embeddings with automatic invalidation

### Key Features
- **Automatic Invalidation**: Cache invalidates when data changes
- **Pathlib Integration**: Modern file operations
- **Metadata Tracking**: Version and hash-based validation
- **Error Recovery**: Graceful handling of cache corruption

### Main Methods
- `save_embeddings(embeddings, data_hash, version)`: Save embeddings with metadata
- `load_embeddings(current_data_hash)`: Load if cache is valid
- `clear_cache()`: Remove all cached data
- `get_cache_info()`: Get cache metadata
- `is_cache_valid(current_data_hash)`: Check cache validity
- `get_cache_size()`: Get cache size in bytes

### Cache Structure
```
cache/
├── tool_embeddings.pkl      # Tool embeddings data
├── tool_metadata.json       # Tool cache metadata
├── negative_embeddings.pkl  # Negative examples data
└── negative_metadata.json   # Negative cache metadata
```

### Usage Example
```python
from agents.embedding_cache import EmbeddingCache

# Initialize cache
cache = EmbeddingCache(cache_dir="cache", prefix="tool")

# Save embeddings
embeddings = {"example": [0.1, 0.2, 0.3]}
data_hash = "abc123"
success = cache.save_embeddings(embeddings, data_hash, version="1.0")

# Load embeddings
loaded_embeddings = cache.load_embeddings(data_hash)
if loaded_embeddings:
    print("Cache hit!")
else:
    print("Cache miss, rebuilding...")

# Check cache status
cache_info = cache.get_cache_info()
is_valid = cache.is_cache_valid(data_hash)
cache_size = cache.get_cache_size()
```

**[↑ Back to Index](#module-index)**

---

## [Tool Configuration (`tool_config.py`)](#tool-configuration-tool_configpy)
**[↑ Back to Index](#module-index)**

**Purpose**: Configuration-driven tool registration and example management

### Key Components

#### `TOOL_REGISTRY`
Pre-configured tool registry with built-in tools:
- **google_search**: Web search functionality
- **get_page**: Web page content retrieval

#### `TOOL_EXAMPLES`
Positive examples for semantic matching:
- Search-related queries for google_search
- Content retrieval queries for get_page

#### `NEGATIVE_EXAMPLES`
Examples that should NOT trigger tools:
- General conversation
- AI questions
- General knowledge queries
- Creative requests

### Tool Schema Format
```python
TOOL_REGISTRY = {
    "tool_name": {
        "function": actual_function,
        "parameter_schema": {
            "param_name": {
                "type": type_class,
                "required": bool,
                "default": default_value,
                "description": "Parameter description"
            }
        },
        "description": "Tool description"
    }
}
```

### Usage Example
```python
from agents.tool_config import TOOL_REGISTRY, TOOL_EXAMPLES, NEGATIVE_EXAMPLES

# Access built-in tools
search_tool = TOOL_REGISTRY["google_search"]
print(search_tool["description"])  # "Search the web for current information"

# Get tool examples
search_examples = [example for name, example in TOOL_EXAMPLES if name == "google_search"]
print(search_examples[:3])  # First 3 search examples

# Check negative examples
print("hello" in NEGATIVE_EXAMPLES)  # True
```

**[↑ Back to Index](#module-index)**

---

## [System Prompts (`prompts.py`)](#system-prompts-promptspy)
**[↑ Back to Index](#module-index)**

**Purpose**: System prompts and instructions for the Datahouse agent

### Key Components

#### `SYSTEM_PROMPT`
The main system prompt that defines the agent's capabilities and behavior:

```python
SYSTEM_PROMPT = """You are Datahouse, an intelligent agent with web access capabilities. You can search for current information and analyze web content to provide accurate, up-to-date answers.

Your capabilities:
- Search the web for current information using Google Search
- Retrieve and analyze content from web pages
- Provide comprehensive, factual responses based on real-time data

When users ask for current information, recent events, or need to verify facts, use your web access tools to provide accurate answers. For general knowledge questions that don't require current data, you can respond directly.

Always be helpful, accurate, and transparent about your sources when using web tools."""
```

### Features
- **Clear Capabilities**: Defines what the agent can do
- **Tool Usage Guidelines**: When to use web tools vs. direct responses
- **Transparency**: Emphasizes source attribution
- **Concise Format**: Optimized for performance

### Usage Example
```python
from agents.prompts import SYSTEM_PROMPT

# Use in agent initialization
from agents.core import DatahouseAgent, AgentConfig

config = AgentConfig(system_prompt=SYSTEM_PROMPT)
agent = DatahouseAgent(config)

# Customize prompt
custom_prompt = SYSTEM_PROMPT + "\n\nAdditional instruction: Always be concise."
config = AgentConfig(system_prompt=custom_prompt)
```

**[↑ Back to Index](#module-index)**

---

## [Agent Utilities (`utilities/agent_utils.py`)](#agent-utilities-utilitiesagent_utilspy)
**[↑ Back to Index](#module-index)**

**Purpose**: Shared utility functions for common operations across the agents module

### Key Components

#### `ValidationResult` Dataclass
```python
@dataclass
class ValidationResult:
    is_valid: bool
    validated_params: Dict[str, Any]
    errors: List[str]
```
- **Purpose**: Result of parameter validation
- **Fields**: Validation status, validated parameters, and error messages

### Core Functions

#### Text Processing
- `extract_query_from_message(message)`: Remove search words from message
- `extract_urls_from_text(text)`: Extract all URLs using regex
- `extract_first_url_from_text(text)`: Get first URL from text

#### Type Conversion
- `convert_value_to_type(value, target_type)`: Convert value to target type
- `validate_and_convert_parameters(parameters, schema)`: Validate and convert parameters

#### Parameter Extraction
- `extract_parameters_simple(message, schema)`: Simple parameter extraction
- `validate_parameters(parameters, schema)`: Legacy validation function

### Constants
```python
SEARCH_WORDS = ["search for", "search about", "find", "look up", "get", "show me", "what is", "who is"]
URL_PATTERN = r'https?://[^\s]+'
```

### Usage Example
```python
from utilities.agent_utils import (
    extract_query_from_message,
    extract_first_url_from_text,
    convert_value_to_type,
    validate_and_convert_parameters
)

# Extract query
query = extract_query_from_message("search for python tutorials")
print(query)  # "python tutorials"

# Extract URL
url = extract_first_url_from_text("Check out https://example.com for more info")
print(url)  # "https://example.com"

# Type conversion
value = convert_value_to_type("42", int)
print(value)  # 42

# Parameter validation
params = {"query": "test", "limit": "10"}
schema = {
    "query": {"type": str, "required": True},
    "limit": {"type": int, "required": False, "default": 5}
}
result = validate_and_convert_parameters(params, schema)
print(result.is_valid)  # True
print(result.validated_params)  # {'query': 'test', 'limit': 10}
```

**[↑ Back to Index](#module-index)**

---

## Integration Examples

### Complete Workflow
```python
from agents.core import DatahouseAgent, AgentConfig
from agents.tool_config import TOOL_REGISTRY

# Initialize agent
config = AgentConfig(cache_dir="cache")
agent = DatahouseAgent(config)

# Process user request
user_message = "search for latest news about artificial intelligence"
response = agent.process(user_message)

# Get tool information
tool_info = agent.get_tool_info()
print(f"Available tools: {tool_info['available_tools']}")
```

### Custom Tool Registration
```python
def custom_weather_function(city: str, units: str = "celsius"):
    return f"Weather for {city} in {units}"

weather_schema = {
    "city": {"type": str, "required": True, "description": "City name"},
    "units": {"type": str, "required": False, "default": "celsius", "description": "Temperature units"}
}

agent.register_tool("weather", custom_weather_function, weather_schema, "Get weather information")
```

### Cache Management
```python
# Clear all caches
agent.tool_selector.clear_cache()

# Get cache information
cache_info = agent.tool_selector.get_cache_info()
print(f"Cache size: {cache_info['tool_cache_size']} bytes")
```

## Performance Considerations

### Optimization Features
- **Embedding Caching**: Persistent cache for performance
- **Numpy Integration**: Fast similarity calculations
- **Unified Cache Management**: Efficient cache operations
- **Template-based Prompts**: Optimized LLM interactions

### Memory Usage
- **Lazy Loading**: Embeddings loaded on demand
- **Efficient Data Structures**: Optimized for memory usage
- **Cache Invalidation**: Automatic cleanup of stale data

### Scalability
- **Dynamic Tool Registration**: Add tools without restart
- **Batch Processing**: Efficient parameter extraction
- **Error Recovery**: Graceful handling of failures

## Testing and Validation

### Unit Testing
```python
# Test tool selection
def test_tool_selection():
    selector = ToolSelector(mock_client, "test_cache")
    tools = selector.select_tool("search for information")
    assert len(tools) > 0
    assert tools[0][0] == "google_search"

# Test parameter extraction
def test_parameter_extraction():
    extractor = LLMParameterExtractor(mock_client)
    params = extractor.extract_parameters("search for python", "google_search", schema)
    assert "query" in params
    assert params["query"] == "python"
```

### Integration Testing
```python
# Test complete workflow
def test_agent_workflow():
    agent = DatahouseAgent()
    response = agent.process("search for latest news")
    assert "Tools needed" in response
    assert "google_search" in response
```

## Troubleshooting

### Common Issues

#### Cache Problems
```python
# Clear cache if corrupted
agent.tool_selector.clear_cache()

# Check cache validity
cache_info = agent.tool_selector.get_cache_info()
if not cache_info['tool_cache_valid']:
    print("Cache invalid, rebuilding...")
```

#### Parameter Extraction Issues
```python
# Use fallback extraction
from agents.utils import extract_parameters_simple
params = extract_parameters_simple(message, schema)

# Check LLM availability
try:
    params = agent.tool_registry.extract_parameters(message, tool_name)
except Exception as e:
    print(f"LLM extraction failed: {e}")
```

#### Tool Registration Issues
```python
# Verify tool exists
if tool_name in agent.get_available_tools():
    tool_info = agent.tool_registry.get_tool(tool_name)
    print(f"Tool schema: {tool_info['parameter_schema']}")
else:
    print(f"Tool '{tool_name}' not found")
```

## Future Enhancements

### Planned Features
- **Async Support**: Parallel processing capabilities
- **Advanced Caching**: Redis integration for distributed caching
- **Dynamic Configuration**: Hot-reloading of configurations
- **Performance Monitoring**: Metrics and analytics

### Extension Points
- **Custom Embedding Models**: Support for different embedding providers
- **Advanced Tool Types**: Support for complex tool workflows
- **Plugin System**: Dynamic tool loading from external sources
- **Multi-modal Support**: Image and audio processing capabilities

---

## Summary

The `/agents` module provides a comprehensive, optimized framework for intelligent tool selection and execution. With its modular architecture, performance optimizations, and extensive documentation, it serves as the foundation for the Datahouse system's AI capabilities.

**Key Strengths**:
- **Semantic Understanding**: LLM-powered tool selection
- **Performance Optimized**: Caching and efficient algorithms
- **Extensible**: Easy to add new tools and capabilities
- **Robust**: Comprehensive error handling and recovery
- **Well Documented**: Clear APIs and usage examples

For more information about the optimization work done on this module, see the [Optimization Log](../docs/optimization_log.md). 