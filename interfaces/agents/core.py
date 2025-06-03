from interfaces.agents.openai_context import OpenAIChatContextManager

class DatahouseAgent():
    """
    The DatahouseAgent is the primary entry point and orchestrator for the Datahouse system.

    It is a broadly knowledgeable agent with access to the web, enabling it to interpret user requests, coordinate workflows, and autonomously solve a wide range of problems. 
    """

    def __init__(self):
        """
        Initialize the DatahouseAgent's OpenAI chat context.
        """
        self.context_manager = OpenAIChatContextManager(system_prompt=(
            "You are the DatahouseAgent, the primary entry point and orchestrator for the Datahouse system. "
        ))

    def process(self, message: str) -> str:
        """
        Process a user message by leveraging the agent's knowledge and web access to generate a response.
        
        Args:
            message: The user input or request to process.
        Returns:
            The generated response based on available resources and reasoning.
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        self.context_manager.add_user_message(str)
        return self.context_manager.get_response()
