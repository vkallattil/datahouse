from typing import Optional
from openai import OpenAI, OpenAIError
from utilities.config import OPENAI_API_KEY

class OpenAIClient:
    """A client for interacting with OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client.
        
        Args:
            api_key: Optional API key. If not provided, will use OPENAI_API_KEY from config.
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in environment variables.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_response(self, prompt: str, model: str = "gpt-4.1-nano") -> str:
        """Generate a text response using the OpenAI API.
        
        Args:
            prompt: The input prompt to send to the model.
            model: The model to use (default: "gpt-4").
            
        Returns:
            The generated text response.
            
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            raise OpenAIError(f"Error generating response: {str(e)}")

# Create a default instance for convenience
# Note: This will raise an error if OPENAI_API_KEY is not set
try:
    openai_client = OpenAIClient()
except ValueError as e:
    # This allows the module to be imported without an API key
    # The error will be raised when actually trying to use the client
    openai_client = None
