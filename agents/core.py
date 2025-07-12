"""
Optimized DatahouseAgent - primary entry point and orchestrator for the Datahouse system.
"""

from dataclasses import dataclass
from openai import OpenAI
from typing import List
from .prompts import SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the DatahouseAgent."""
    system_prompt: str = SYSTEM_PROMPT

@dataclass
class Message:
    """Represents a chat message."""
    role: str
    content: str

class DatahouseAgent:
    """Optimized DatahouseAgent with simplified structure and better performance."""
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.client = OpenAI()
        self.messages = [Message("developer", self.config.system_prompt)]
    
    def clear_messages(self) -> None:
        """Clear chat history, keeping system prompt."""
        self.messages = [Message("developer", self.config.system_prompt)]

    def process(self, message: str) -> str:
        """Process user message with a single GPT-4.1 nano chat completion."""
        self.messages.append(Message("user", message))

        completion = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": m.role, "content": m.content} for m in self.messages]
        )

        response = completion.choices[0].message.content

        self.messages.append(Message("assistant", response))

        return response