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
Configuration object for agent initialization with system prompt and cache directory settings.

#### `Message` Dataclass
Simple message container with role and content fields for chat history management.

#### `DatahouseAgent` Class
Main agent class that orchestrates tool selection, parameter extraction, and execution.

**Key Methods:**
- `process(message)`: Process user messages and return tool selection or response
- `register_tool(name, function, schema, description)`: Register new tools dynamically
- `get_tool_info()`: Get comprehensive information about all tools and cache status

### Usage Example
```python
from agents.core import DatahouseAgent, AgentConfig

# Initialize agent with custom configuration
config = AgentConfig(
    system_prompt="You are a helpful AI assistant with web access.",
    cache_dir="my_cache"
)
agent = DatahouseAgent(config)

# Process user requests
response = agent.process("search for latest news about AI")
print(response)  # "Tools needed: google_search (0.856)"

# Register custom tools
def weather_tool(city: str, units: str = "celsius"):
    return f"Weather for {city} in {units}"

weather_schema = {
    "city": {"type": str, "required": True, "description": "City name"},
    "units": {"type": str, "required": False, "default": "celsius"}
}

agent.register_tool("weather", weather_tool, weather_schema, "Get weather information")

# Get system information
info = agent.get_tool_info()
print(f"Available tools: {info['available_tools']}")
```

**[↑ Back to Index](#module-index)**

---

## [Tool Selector (`tool_selector.py`)](#tool-selector-tool_selectorpy)
**[↑ Back to Index](#module-index)**

**Purpose**: Semantic tool selection using embeddings and similarity matching

### Key Components

#### `EmbeddingData` Dataclass
Container for embeddings and data hash for cache validation.

#### `UnifiedCacheManager` Class
Unified cache management for both tool and negative embeddings with save/load operations.

#### `ToolSelector` Class
Main tool selection component using semantic similarity with OpenAI embeddings.

**Key Methods:**
- `select_tool(message, threshold, max_tools)`: Select appropriate tools for user message
- `clear_cache()`: Clear all cached embeddings
- `get_cache_info()`: Get comprehensive cache information

### Usage Example
```python
from agents.tool_selector import ToolSelector
from openai import OpenAI

# Initialize tool selector with OpenAI client
client = OpenAI(api_key="your-api-key")
selector = ToolSelector(client, cache_dir="embeddings_cache")

# Select tools for user message
tools = selector.select_tool(
    "find the latest news about climate change",
    threshold=0.5,
    max_tools=3
)

for tool_name, similarity_score in tools:
    print(f"{tool_name}: {similarity_score:.3f}")

# Manage cache
cache_info = selector.get_cache_info()
print(f"Embedding count: {cache_info['embedding_count']}")
print(f"Cache size: {cache_info['tool_cache_size']} bytes")

# Clear cache if needed
selector.clear_cache()
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

### `ToolRegistry` Class
Manages tool registration, parameter extraction, validation, and execution.

**Key Methods:**
- `register_tool(name, function, schema, description)`: Register new tools
- `extract_parameters(message, tool_name)`: Extract parameters using LLM or fallback
- `execute_tool(tool_name, parameters)`: Execute tools with validation
- `get_tool_info()`: Get information about all registered tools

### Usage Example
```python
from agents.tool_registry import ToolRegistry
from openai import OpenAI

# Initialize registry with OpenAI client for LLM extraction
client = OpenAI(api_key="your-api-key")
registry = ToolRegistry(client)

# Register a custom tool
def stock_price_tool(symbol: str, exchange: str = "NASDAQ"):
    return f"Stock price for {symbol} on {exchange}"

stock_schema = {
    "symbol": {"type": str, "required": True, "description": "Stock symbol"},
    "exchange": {"type": str, "required": False, "default": "NASDAQ"}
}

registry.register_tool("stock_price", stock_price_tool, stock_schema, "Get stock prices")

# Extract parameters from user message
params = registry.extract_parameters(
    "get stock price for AAPL on NYSE",
    "stock_price"
)
print(params)  # {'symbol': 'AAPL', 'exchange': 'NYSE'}

# Execute the tool
success, result, error = registry.execute_tool("stock_price", params)
if success:
    print(f"Result: {result}")
else:
    print(f"Error: {error}")

# Get all tool information
tool_info = registry.get_tool_info()
for name, info in tool_info.items():
    print(f"{name}: {info['description']}")
```

**[↑ Back to Index](#module-index)**

---

## [Parameter Extractor (`parameter_extractor.py`)](#parameter-extractor-parameter_extractorpy)
**[↑ Back to Index](#module-index)**

**Purpose**: LLM-based intelligent parameter extraction from user messages

### Key Components

#### `ExtractionConfig` Dataclass
Configuration for LLM-based parameter extraction with model, temperature, and token settings.

#### `LLMParameterExtractor` Class
Extracts parameters from user messages using LLM intelligence with fallback mechanisms.

**Key Methods:**
- `extract_parameters(message, tool_name, schema)`: Extract parameters using LLM
- `batch_extract(messages, tool_name, schema)`: Extract parameters for multiple messages

### Usage Example
```python
from agents.parameter_extractor import LLMParameterExtractor, ExtractionConfig
from openai import OpenAI

# Initialize extractor with custom configuration
client = OpenAI(api_key="your-api-key")
config = ExtractionConfig(
    model="gpt-4",
    temperature=0.1,
    max_tokens=200
)
extractor = LLMParameterExtractor(client, config)

# Define parameter schema
schema = {
    "query": {"type": str, "required": True, "description": "Search query"},
    "limit": {"type": int, "required": False, "default": 10, "description": "Result limit"},
    "language": {"type": str, "required": False, "default": "en", "description": "Language"}
}

# Extract parameters from user message
params = extractor.extract_parameters(
    "search for machine learning tutorials with 20 results in Spanish",
    "search_tool",
    schema
)
print(params)  # {'query': 'machine learning tutorials', 'limit': 20, 'language': 'es'}

# Batch extraction for multiple messages
messages = [
    "search for python tutorials",
    "find AI articles with 15 results",
    "get weather for London"
]

batch_params = extractor.batch_extract(messages, "search_tool", schema)
for i, params in enumerate(batch_params):
    print(f"Message {i+1}: {params}")
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

### `EmbeddingCache` Class
Manages persistent caching of embeddings with automatic validation.

**Key Methods:**
- `save_embeddings(embeddings, data_hash, version)`: Save embeddings with metadata
- `load_embeddings(current_data_hash)`: Load embeddings if cache is valid
- `clear_cache()`: Clear cached embeddings
- `get_cache_info()`: Get cache metadata

### Usage Example
```python
from agents.embedding_cache import EmbeddingCache

# Initialize cache with custom directory and prefix
cache = EmbeddingCache(cache_dir="my_embeddings", prefix="custom")

# Prepare embeddings and data hash
embeddings = {
    "example1": [0.1, 0.2, 0.3, 0.4],
    "example2": [0.5, 0.6, 0.7, 0.8]
}
data_hash = "abc123def456"

# Save embeddings to cache
success = cache.save_embeddings(embeddings, data_hash, version="1.0")
print(f"Save successful: {success}")

# Load embeddings from cache
loaded_embeddings = cache.load_embeddings(data_hash)
if loaded_embeddings:
    print("Cache hit! Loaded embeddings:")
    for key, embedding in loaded_embeddings.items():
        print(f"  {key}: {embedding[:2]}...")  # Show first 2 values
else:
    print("Cache miss - embeddings not found or invalid")

# Get cache information
cache_info = cache.get_cache_info()
if cache_info:
    print(f"Data hash: {cache_info['data_hash']}")
    print(f"Version: {cache_info['version']}")
    print(f"Cache size: {cache.get_cache_size()} bytes")

# Clear cache if needed
cache.clear_cache()
```

**[↑ Back to Index](#module-index)**

---

## [Agent Utilities (`utilities/agent_utils.py`)](#agent-utilities-utilitiesagent_utilspy)
**[↑ Back to Index](#module-index)**

**Purpose**: Shared utility functions for common operations across the agents module

### Key Components

#### `ValidationResult` Dataclass
Container for validation results with status, validated parameters, and error messages.

### Core Functions

#### Text Processing Functions
- `extract_query_from_message(message)`: Extract search query by removing common search words
- `extract_urls_from_text(text)`: Extract all URLs from text using regex
- `extract_first_url_from_text(text)`: Extract the first URL from text

#### Type Conversion Functions
- `convert_value_to_type(value, target_type)`: Convert value to target type with error handling
- `validate_and_convert_parameters(parameters, schema)`: Validate and convert parameters according to schema

#### Parameter Extraction Functions
- `extract_parameters_simple(message, schema)`: Simple parameter extraction as fallback
- `validate_parameters(parameters, schema)`: Legacy validation function for backward compatibility

### Usage Example
```python
from utilities.agent_utils import (
    extract_query_from_message,
    extract_urls_from_text,
    validate_and_convert_parameters,
    ValidationResult
)

# Text processing
query = extract_query_from_message("search for python tutorials online")
print(query)  # "python tutorials online"

urls = extract_urls_from_text("Check out https://example.com and https://test.com")
print(urls)  # ['https://example.com', 'https://test.com']

# Parameter validation
params = {"query": "test", "limit": "10", "enabled": "true"}
schema = {
    "query": {"type": str, "required": True, "description": "Search query"},
    "limit": {"type": int, "required": False, "default": 5, "description": "Result limit"},
    "enabled": {"type": bool, "required": False, "default": True, "description": "Enable feature"}
}

result = validate_and_convert_parameters(params, schema)
if result.is_valid:
    print(f"Validated params: {result.validated_params}")
    # Output: {'query': 'test', 'limit': 10, 'enabled': True}
else:
    print(f"Validation errors: {result.errors}")

# Type conversion
value = convert_value_to_type("42", int)
print(value)  # 42

value = convert_value_to_type("3.14", float)
print(value)  # 3.14

value = convert_value_to_type("true", bool)
print(value)  # True
```

**[↑ Back to Index](#module-index)**

---

## [Tool Configuration (`tool_config.py`)](#tool-configuration-tool_configpy)
**[↑ Back to Index](#module-index)**

**Purpose**: Configuration-driven tool registration and example management

### Key Components

#### `TOOL_REGISTRY`
Pre-configured tool registry with built-in tools like `google_search` and `get_page`.

#### `TOOL_EXAMPLES`
Positive examples for semantic matching to train the tool selector.

#### `NEGATIVE_EXAMPLES`
Examples that should NOT trigger tools (general conversation, AI questions, etc.).

### Usage Example
```python
from agents.tool_config import TOOL_REGISTRY, TOOL_EXAMPLES, NEGATIVE_EXAMPLES

# Access built-in tools
search_tool = TOOL_REGISTRY["google_search"]
print(search_tool["description"])  # "Search the web for current information"

# Get tool schema
schema = search_tool["parameter_schema"]
required_params = [k for k, v in schema.items() if v['required']]
print(f"Required parameters: {required_params}")  # ['query']

# Work with tool examples
search_examples = [example for name, example in TOOL_EXAMPLES if name == "google_search"]
print(f"Search examples: {search_examples[:3]}")

# Check negative examples
query = "hello"
if query in NEGATIVE_EXAMPLES:
    print("This query should not trigger any tools")

# Add custom tools to registry
def custom_tool_function(param1: str, param2: int = 10):
    return f"Processing {param1} with {param2}"

custom_schema = {
    "param1": {"type": str, "required": True, "description": "First parameter"},
    "param2": {"type": int, "required": False, "default": 10, "description": "Second parameter"}
}

TOOL_REGISTRY["custom_tool"] = {
    "function": custom_tool_function,
    "parameter_schema": custom_schema,
    "description": "Custom tool description"
}

# Add examples for new tool
TOOL_EXAMPLES.extend([
    ("custom_tool", "use custom tool with parameter"),
    ("custom_tool", "process with custom tool"),
])
```

**[↑ Back to Index](#module-index)**

---

## [System Prompts (`prompts.py`)](#system-prompts-promptspy)
**[↑ Back to Index](#module-index)**

**Purpose**: System prompts and instructions for the Datahouse agent

### Key Components

#### `SYSTEM_PROMPT`
The main system prompt that defines the agent's capabilities and behavior.

### Usage Example
```python
from agents.prompts import SYSTEM_PROMPT
from agents.core import DatahouseAgent, AgentConfig

# Use default system prompt
config = AgentConfig(system_prompt=SYSTEM_PROMPT)
agent = DatahouseAgent(config)

# Customize the prompt
custom_prompt = SYSTEM_PROMPT + """

Additional guidelines:
- Always provide detailed explanations
- Include relevant code examples when appropriate
- Verify information from multiple sources
"""

config = AgentConfig(system_prompt=custom_prompt)
agent = DatahouseAgent(config)

# Create specialized prompts
research_prompt = """You are Datahouse, a research assistant with web access capabilities.

Your primary focus is on:
- Comprehensive research and analysis
- Source verification and validation
- Detailed, well-structured responses
- Academic and professional standards

When conducting research:
1. Use multiple sources for verification
2. Provide detailed citations
3. Include relevant context and background
4. Highlight any limitations or uncertainties

Always be thorough, accurate, and transparent about your sources."""

# Use specialized prompt
config = AgentConfig(system_prompt=research_prompt)
research_agent = DatahouseAgent(config)
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
from utilities.agent_utils import extract_parameters_simple
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