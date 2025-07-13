from dataclasses import dataclass
from openai import OpenAI
import logging
from pydantic import BaseModel
from typing import Literal
from datetime import datetime
import json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""
Context:
Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Instructions:
Determine if the user's query can be resolved with the model's knowledge base up until October 2023. If so, return no instructions. Otherwise, return a set of instructions that will be executed to resolve the user's query step by step.
"""

@dataclass
class Message:
    role: str
    content: str    

class SearchInstruction(BaseModel):
    name: Literal["search_and_read"]
    description: Literal["Search the web for information beyond your October 2023 training cutoff."]

class Instructions(BaseModel):
    instructions: list[SearchInstruction]

class DatahouseAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [Message("developer", SYSTEM_PROMPT)]
    
    def clear_messages(self) -> None:
        self.messages = [Message("developer", SYSTEM_PROMPT)]

    def add_message(self, message: Message) -> None:
        # Add message with timestamp
        self.messages.append(Message(message.role, message.content + f"\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))

    def process(self, message: str) -> str:
        self.add_message(Message("user", message))
        
        completion = self.client.chat.completions.parse(
            model="gpt-4.1-nano",
            messages=[{"role": m.role, "content": m.content} for m in self.messages],
            response_format=Instructions
        )

        instructions = completion.choices[0].message.parsed.instructions

        response = json.dumps([i.model_dump() for i in instructions], indent=2)

        self.add_message(Message("assistant", response))
        
        return response