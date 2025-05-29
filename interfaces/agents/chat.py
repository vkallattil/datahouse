from interfaces.agents.base import Agent, Message
from typing import Optional, Any
from openai import OpenAI, OpenAIError
from utilities.env import OPENAI_API_KEY

class ChatAgent(Agent[str, str]):
    def __init__(self, system_prompt: str):
        super().__init__()

        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in environment variables.")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = system_prompt
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
    
    def process(self, message: Message[str]) -> str:
        """Generate a text response using the OpenAI API.
        
        Args:
            message: The input prompt to send to the model.
            
        Returns:
            The generated text response.
            
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        try:
            self.messages.append({
              "role": "user",
              "content": message.content
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