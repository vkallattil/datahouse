from interfaces.agents.entities import AgentFactory
from interfaces.agents.chat import ChatAgent

AgentFactory.register("chat", ChatAgent)
