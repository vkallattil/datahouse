"""
Agent utility functions for parameter extraction, validation, and type conversion.
Consolidated functionality for the agents module.
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass

# Common constants
SEARCH_WORDS = ["search for", "search about", "find", "look up", "get", "show me", "what is", "who is"]
URL_PATTERN = r'https?://[^\s]+'

@dataclass
class ValidationResult:
    """Result of parameter validation."""
    is_valid: bool
    validated_params: Dict[str, Any]
    errors: List[str]

def extract_query_from_message(message: str) -> str:
    """Extract search query by removing common search words."""
    query = message.lower()
    for word in SEARCH_WORDS:
        query = query.replace(word, "").strip()
    return query if query else message

def extract_urls_from_text(text: str) -> List[str]:
    """Extract all URLs from text using regex."""
    return re.findall(URL_PATTERN, text)

def extract_first_url_from_text(text: str) -> Optional[str]:
    """Extract the first URL from text."""
    urls = extract_urls_from_text(text)
    return urls[0] if urls else None

def convert_value_to_type(value: Any, target_type: type) -> Any:
    """Convert value to target type with error handling."""
    if value is None or isinstance(value, target_type):
        return value
    
    try:
        if target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == bool:
            return bool(value)
        elif target_type == str:
            return str(value)
        else:
            return value
    except (ValueError, TypeError):
        return value

def validate_and_convert_parameters(parameters: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
    """Validate and convert parameters according to schema."""
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
        
        # Type validation and conversion
        if param_type:
            converted_value = convert_value_to_type(param_value, param_type)
            if not isinstance(converted_value, param_type) and param_value is not None:
                errors.append(f"Parameter '{param_name}' must be of type {param_type.__name__}")
                continue
            param_value = converted_value
        
        validated_params[param_name] = param_value
    
    return ValidationResult(len(errors) == 0, validated_params, errors)

def extract_parameters_simple(message: str, parameter_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Simple parameter extraction as fallback when LLM is not available."""
    extracted_params = {}
    
    for param_name, param_config in parameter_schema.items():
        required = param_config.get("required", False)
        default = param_config.get("default")
        
        # Simple extraction based on parameter name
        if param_name == "query":
            extracted_params[param_name] = extract_query_from_message(message)
        elif param_name == "url":
            extracted_params[param_name] = extract_first_url_from_text(message)
        else:
            extracted_params[param_name] = message
        
        # Apply defaults for missing optional parameters
        if extracted_params[param_name] is None and not required:
            extracted_params[param_name] = default
    
    return extracted_params

# Legacy function for backward compatibility
def validate_parameters(parameters: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """Legacy validation function for backward compatibility."""
    result = validate_and_convert_parameters(parameters, schema)
    return result.is_valid, result.validated_params, result.errors 