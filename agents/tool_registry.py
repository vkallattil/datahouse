"""
Optimized tool registry system for dynamic tool registration and execution.
"""

from typing import Dict, Any, Callable, List, Tuple, Optional
from .tool_config import TOOL_REGISTRY
from .parameter_extractor import LLMParameterExtractor
from utilities.agent_utils import validate_and_convert_parameters, extract_parameters_simple

class ToolRegistry:
    """Optimized tool registry with simplified architecture and better performance."""
    
    def __init__(self, client=None):
        self.tools = TOOL_REGISTRY.copy()
        self.parameter_extractor = LLMParameterExtractor(client) if client else None
    
    def register_tool(self, name: str, function: Callable, parameter_schema: Dict[str, Any], description: str = "") -> None:
        """Register a new tool with the registry."""
        self.tools[name] = {
            "function": function,
            "parameter_schema": parameter_schema,
            "description": description
        }
    
    def unregister_tool(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self.tools:
            del self.tools[name]
            return True
        return False
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool configuration by name."""
        return self.tools.get(name)
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tool names."""
        return list(self.tools.keys())
    
    def extract_parameters(self, message: str, tool_name: str) -> Dict[str, Any]:
        """Extract parameters for a tool from a user message."""
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return {}
        
        parameter_schema = tool_config.get("parameter_schema", {})
        
        # Use LLM-based extraction if available
        if self.parameter_extractor:
            try:
                return self.parameter_extractor.extract_parameters(
                    message, tool_name, parameter_schema
                )
            except Exception as e:
                print(f"LLM extraction failed, falling back to simple extraction: {e}")
        
        # Fallback to simple extraction using utility function
        return extract_parameters_simple(message, tool_name, parameter_schema)
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Validate parameters against the tool's schema (legacy interface)."""
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return False, {}, ["Tool not found"]
        
        schema = tool_config.get("parameter_schema", {})
        result = validate_and_convert_parameters(parameters, schema)
        return result.is_valid, result.validated_params, result.errors
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """Execute a tool with the given parameters."""
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return False, None, f"Tool '{tool_name}' not found"
        
        # Validate parameters
        is_valid, validated_params, errors = self.validate_parameters(tool_name, parameters)
        if not is_valid:
            return False, None, f"Parameter validation failed: {', '.join(errors)}"
        
        try:
            # Execute the tool
            function = tool_config["function"]
            result = function(**validated_params)
            return True, result, ""
        except Exception as e:
            return False, None, f"Tool execution failed: {str(e)}"
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about all registered tools."""
        info = {}
        for name, config in self.tools.items():
            info[name] = {
                "description": config.get("description", ""),
                "parameters": list(config.get("parameter_schema", {}).keys()),
                "required_parameters": [
                    param for param, schema in config.get("parameter_schema", {}).items()
                    if schema.get("required", False)
                ]
            }
        return info 