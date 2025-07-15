import json
import asyncio
import logging
from openai import OpenAI
from typing import Literal
from datetime import datetime
from modules.search import search_and_read
from modules.notes import read_notes, write_notes

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "Respond to the user as if you are a helpful assistant. Each user message is prepended with a timestamp for information purposes - do not include the timestamp in your response."

class DatahouseAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [{"role": "developer", "content": SYSTEM_PROMPT}]
        self.tools = [{
            "type": "function",
            "name": "search_and_read",
            "description": "Search the web for up to date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": True
        }, {
            "type": "function",
            "name": "read_notes",
            "description": "Read the notes file.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }, {
            "type": "function",
            "name": "write_notes",
            "description": "Write to the notes file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"}
                },
                "required": ["content"],
                "additionalProperties": False
            },
            "strict": True
        }]
    
    def clear_messages(self) -> None:
        self.messages = [{"role": "developer", "content": SYSTEM_PROMPT}]

    async def process(self, message: str):
        self.messages.append({"role": "user", "content": message})

        stream = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=self.messages,
            stream=True
        )

        response_message = ""

        # If stream is not async, wrap in async generator
        async def async_stream_wrapper(sync_stream):
            loop = asyncio.get_event_loop()
            for chunk in sync_stream:
                yield chunk
        
        # Use the wrapper if needed
        stream_gen = async_stream_wrapper(stream)

        async for chunk in stream_gen:
            content = getattr(chunk.choices[0].delta, 'content', None)
            if content is not None:
                response_message += content
                # Internal processing can go here
                yield content

        self.messages.append({"role": "assistant", "content": response_message})