from interfaces.agents.base import Agent, Message
from interfaces.agents.openai_context import OpenAIChatContextManager
from typing import Optional, Any
from openai import OpenAIError

class ChatAgent(Agent[str, str]):
    """
    Represents a chat agent.
    """
    def __init__(self, system_prompt: str):
        super().__init__()
        self.context_manager = OpenAIChatContextManager(system_prompt)
    
    def clear_messages(self):
        """Clears the message history."""
        self.context_manager.clear_messages()
    
    def process(self, message: Message[str]) -> str:
        """Generate a text response using the OpenAI API.
        
        Args:
            message: The input prompt to send to the model.
        Returns:
            The generated text response.
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        self.context_manager.add_user_message(message.content)
        
        return self.context_manager.get_response()