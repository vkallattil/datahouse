"""
Simple tool registry system for dynamic tool registration and execution.
Handles parameter validation and tool execution without redundant extraction rules.
"""

import re
from typing import Dict, Any, Callable, List, Tuple, Optional
from .tool_config import TOOL_REGISTRY

class ToolRegistry:
    """
    A simple registry for tool registration and execution.
    Handles parameter validation and tool execution.
    """
    
    def __init__(self):
        self.tools = TOOL_REGISTRY.copy()
    
    def register_tool(self, 
                     name: str, 
                     function: Callable, 
                     parameter_schema: Dict[str, Any],
                     description: str = "") -> None:
        """
        Register a new tool with the registry.
        
        Args:
            name: Tool name
            function: The function to execute
            parameter_schema: Schema defining required parameters and types
            description: Tool description
        """
        self.tools[name] = {
            "function": function,
            "parameter_schema": parameter_schema,
            "description": description
        }
    
    def unregister_tool(self, name: str) -> bool:
        """
        Remove a tool from the registry.
        
        Args:
            name: Tool name to remove
            
        Returns:
            True if tool was removed, False if not found
        """
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
        """
        Extract parameters for a tool from a user message.
        Uses simple, tool-specific extraction logic.
        
        Args:
            message: User message
            tool_name: Name of the tool to extract parameters for
            
        Returns:
            Dictionary of extracted parameters
        """
        if tool_name == "google_search":
            return self._extract_search_parameters(message)
        elif tool_name == "get_page":
            return self._extract_url_parameters(message)
        else:
            # For custom tools, return the message as a generic parameter
            return {"message": message}
    
    def _extract_search_parameters(self, message: str) -> Dict[str, Any]:
        """Extract search query from message."""
        # Remove common search-related words to get the core query
        search_words = ["search for", "search about", "find", "look up", "get", "show me", "what is", "who is"]
        query = message.lower()
        for word in search_words:
            query = query.replace(word, "").strip()
        return {"query": query if query else message}
    
    def _extract_url_parameters(self, message: str) -> Dict[str, Any]:
        """Extract URL from message."""
        # Extract URLs using regex
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message)
        if urls:
            return {"url": urls[0]}
        else:
            return {"url": "Please provide a URL to retrieve content from."}
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate parameters against the tool's schema.
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, validated_parameters, error_messages)
        """
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return False, {}, ["Tool not found"]
        
        schema = tool_config.get("parameter_schema", {})
        validated_params = {}
        errors = []
        
        for param_name, param_config in schema.items():
            param_type = param_config.get("type")
            required = param_config.get("required", False)
            default = param_config.get("default")
            
            # Check if parameter is provided
            if param_name not in parameters:
                if required:
                    errors.append(f"Required parameter '{param_name}' is missing")
                    continue
                elif default is not None:
                    validated_params[param_name] = default
                    continue
                else:
                    continue
            
            param_value = parameters[param_name]
            
            # Type validation
            if param_type and not isinstance(param_value, param_type):
                try:
                    # Try to convert the type
                    if param_type == int:
                        param_value = int(param_value)
                    elif param_type == float:
                        param_value = float(param_value)
                    elif param_type == bool:
                        param_value = bool(param_value)
                    elif param_type == str:
                        param_value = str(param_value)
                except (ValueError, TypeError):
                    errors.append(f"Parameter '{param_name}' must be of type {param_type.__name__}")
                    continue
            
            validated_params[param_name] = param_value
        
        return len(errors) == 0, validated_params, errors
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters to pass to the tool
            
        Returns:
            Tuple of (success, result, error_message)
        """
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