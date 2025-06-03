from interfaces.agents.base import Agent, Message
from interfaces.agents.openai_context import OpenAIChatContextManager

class DatahouseAgent(Agent[str, str]):
    """
    The DatahouseAgent is the primary entry point and orchestrator for the Datahouse system.

    It is a broadly knowledgeable agent with access to the web, enabling it to interpret user requests, coordinate workflows, and autonomously solve a wide range of problems. 
    """

    def __init__(self):
        """
        Initialize the DatahouseAgent with a system prompt.
        """
        super().__init__()
        self.system_prompt = (
            "You are the DatahouseAgent, the primary entry point and orchestrator for the Datahouse system. "
        )
        self.context_manager = OpenAIChatContextManager(self.system_prompt)

    def process(self, message: Message[str]) -> str:
        """
        Process a user message by leveraging the agent's knowledge and web access to generate a response.
        
        Args:
            message: The user input or request to process.
        Returns:
            The generated response based on available resources and reasoning.
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        self.context_manager.add_user_message(message.content)
        return self.context_manager.get_response()
