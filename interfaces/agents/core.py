from interfaces.agents.entities import Agent, Message, AgentFactory
from modules.language.clients import OpenAIClient

class CLIAgent(Agent[str, str]):
    def __init__(self):
        super().__init__()
        self.openai_client = OpenAIClient(system_prompt="You are Turret. You talk exactly like Jarvis from Iron Man.")
    
    def process(self, message: Message[str]):
        return self.openai_client.generate_response(message.content)

    def clear_messages(self):
        self.openai_client.clear_messages()

AgentFactory.register("cli", CLIAgent)
