from typing import Optional, Any
from openai import OpenAI, OpenAIError
from utilities.env import OPENAI_API_KEY

class OpenAIClient:
    """A client for interacting with OpenAI's API."""
    
    def __init__(self, system_prompt: Optional[str] = None):
        """Initialize the OpenAI client.
        
        Args:
            api_key: Optional API key. If not provided, will use OPENAI_API_KEY from utilities.
        """

        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in environment variables.")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.messages = [
          {
            "role": "developer",
            "content": system_prompt
          }
        ]

    def clear_messages(self):
        self.messages = [
          {
            "role": "developer",
            "content": self.system_prompt
          }
        ]
    
    def generate_response(self, prompt: str) -> str:
        """Generate a text response using the OpenAI API.
        
        Args:
            prompt: The input prompt to send to the model.
            
        Returns:
            The generated text response.
            
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        try:
            self.messages.append({
              "role": "user",
              "content": prompt
            })

            response = self.client.chat.completions.create(
              model="gpt-4.1-nano",
              messages=self.messages
            )

            self.messages.append({
              "role": "assistant",
              "content": response.choices[0].message.content
            })

            return response.choices[0].message.content

        except OpenAIError as e:
            raise OpenAIError(f"Error generating response: {str(e)}")