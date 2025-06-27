"""
Optimized LLM-based parameter extraction with simplified architecture and better performance.
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from utilities.agent_utils import extract_query_from_message, extract_first_url_from_text, convert_value_to_type

@dataclass
class ExtractionConfig:
    """Configuration for parameter extraction."""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: int = 200
    system_prompt: str = "You are a parameter extraction assistant. Extract parameters from user messages and return them as JSON."

class LLMParameterExtractor:
    """Optimized LLM parameter extractor with simplified architecture."""
    
    def __init__(self, client: OpenAI, config: ExtractionConfig = None):
        self.client = client
        self.config = config or ExtractionConfig()
    
    def extract_parameters(self, message: str, tool_name: str, parameter_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from user message using LLM."""
        try:
            prompt = self._create_prompt(message, tool_name, parameter_schema)
            response = self._call_llm(prompt)
            return self._parse_response(response, parameter_schema)
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            return self._fallback_extraction(message, parameter_schema)
    
    def _create_prompt(self, message: str, tool_name: str, parameter_schema: Dict[str, Any]) -> str:
        """Create extraction prompt using template."""
        schema_text = self._format_schema(parameter_schema)
        
        return f"""Extract parameters for the '{tool_name}' tool from this user message:

User message: "{message}"

Required parameters:
{schema_text}

Instructions:
1. Analyze the user message and extract the relevant parameters
2. Return ONLY a valid JSON object with the extracted parameters
3. Use null for missing optional parameters
4. Ensure the JSON is properly formatted

Example response format:
{{
    "param1": "extracted_value",
    "param2": null
}}

Extracted parameters (JSON only):"""
    
    def _format_schema(self, parameter_schema: Dict[str, Any]) -> str:
        """Format parameter schema for prompt."""
        schema_lines = []
        for param_name, param_config in parameter_schema.items():
            param_type = param_config.get("type", "any").__name__
            required = "required" if param_config.get("required", False) else "optional"
            description = param_config.get("description", "")
            default = param_config.get("default")
            
            param_desc = f"- {param_name} ({param_type}, {required})"
            if description:
                param_desc += f": {description}"
            if default is not None:
                param_desc += f" (default: {default})"
            
            schema_lines.append(param_desc)
        
        return "\n".join(schema_lines)
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with error handling."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM API call failed: {e}")
            raise
    
    def _parse_response(self, content: str, parameter_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response and extract parameters."""
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            return {}
        
        try:
            extracted_params = json.loads(json_match.group())
            return self._clean_parameters(extracted_params, parameter_schema)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {content}")
            return {}
    
    def _clean_parameters(self, extracted_params: Dict[str, Any], parameter_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate extracted parameters."""
        cleaned_params = {}
        
        for param_name, param_config in parameter_schema.items():
            param_type = param_config.get("type")
            required = param_config.get("required", False)
            default = param_config.get("default")
            
            # Get extracted value
            extracted_value = extracted_params.get(param_name)
            
            # Handle missing values
            if extracted_value is None or extracted_value == "null":
                if required:
                    extracted_value = self._extract_fallback(param_name, extracted_params)
                else:
                    extracted_value = default
            
            # Type conversion
            if extracted_value is not None and param_type:
                converted_value = convert_value_to_type(extracted_value, param_type)
                if isinstance(converted_value, param_type):
                    extracted_value = converted_value
                else:
                    extracted_value = str(extracted_value)
            
            cleaned_params[param_name] = extracted_value
        
        return cleaned_params
    
    def _extract_fallback(self, param_name: str, content: Dict[str, Any]) -> Optional[str]:
        """Fallback extraction when LLM doesn't provide a value."""
        if param_name == "query":
            # Try to extract from any string value in the content
            for value in content.values():
                if isinstance(value, str) and value != "null":
                    return extract_query_from_message(value)
        elif param_name == "url":
            # Look for URL in any string value
            for value in content.values():
                if isinstance(value, str) and value != "null":
                    url = extract_first_url_from_text(value)
                    if url:
                        return url
        return None
    
    def _fallback_extraction(self, message: str, parameter_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback extraction when LLM fails."""
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
    
    def batch_extract(self, messages: List[str], tool_name: str, parameter_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract parameters for multiple messages in batch."""
        return [
            self.extract_parameters(message, tool_name, parameter_schema)
            for message in messages
        ] 