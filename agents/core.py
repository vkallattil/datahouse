from openai import OpenAI
from .prompts import SYSTEM_PROMPT, PLAN_PROMPT_TEMPLATE

class DatahouseAgent():
    """
    The DatahouseAgent is the primary entry point and orchestrator for the Datahouse system.

    It is a broadly knowledgeable agent with access to the web, enabling it to interpret user requests, coordinate workflows, and autonomously solve a wide range of problems. 
    """

    def __init__(self):
        """
        Initialize the DatahouseAgent's OpenAI chat context.
        """

        self.system_prompt = SYSTEM_PROMPT

        self.messages = [
            {"role": "developer", "content": self.system_prompt}
        ]

        self.client = OpenAI()

    def clear_messages(self):
        """Clear the chat history."""
        self.messages = [
            {"role": "developer", "content": self.system_prompt}
        ]

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
        
        # Create a plan to resolve the user's request

        plan_prompt = PLAN_PROMPT_TEMPLATE.format(message=message)
        
        plan = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.0,
            messages=[
                {"role": "developer", "content": self.system_prompt},
                {"role": "user", "content": plan_prompt}
            ]
        ).choices[0].message.content

        # Execute the plan

        return plan
