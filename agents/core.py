import json
import asyncio
import logging
from openai import OpenAI
from typing import Literal
from datetime import datetime
from modules.search import search_and_read
from modules.notes import read_notes, write_notes

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "Respond to the user as if you are a helpful assistant."

async def async_stream_wrapper(sync_stream):
    loop = asyncio.get_event_loop()
    for chunk in sync_stream:
        yield chunk

class DatahouseAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [{"role": "developer", "content": SYSTEM_PROMPT}]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_and_read",
                    "description": "Search the web for up to date information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                },
                "strict": True
            },
            {
                "type": "function",
                "function": {
                    "name": "read_notes",
                    "description": "Read the notes file.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
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
                }
            }
        ]
    
    def clear_messages(self) -> None:
        self.messages = [{"role": "developer", "content": SYSTEM_PROMPT}]

    async def process(self, message: str):

        # Add the user message to the message log.
        self.messages.append({"role": "user", "content": message})

        response_message = "" # Final assistant response message sent to the user.
        final_tool_calls = {} # Final constructed tool call executions from tool call deltas 
        response_completed = False # Indicator for if user message response cycle is complete

        while not response_completed:

            stream = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=self.messages,
                tools=self.tools,
                stream=True
            )

            stream_gen = async_stream_wrapper(stream)

            print("Stream started...")

            async for chunk in stream_gen:
                # Check if chunks contain tool calls, content, or neither
                delta_calls = chunk.choices[0].delta.tool_calls
                delta_content = chunk.choices[0].delta.content

                if delta_calls != None:
                    for tool_call in delta_calls:
                        index = tool_call.index

                        if index not in final_tool_calls:
                            final_tool_calls[index] = tool_call
                            self.messages.append(chunk.choices[0].delta)

                        final_tool_calls[index].function.arguments += tool_call.function.arguments

                        yield tool_call.function.arguments
                    
                elif delta_content != None:
                    response_message += delta_content

                    yield delta_content

                elif delta_calls == None and delta_content == None and len(final_tool_calls.values()) > 0:
                    print()
                    for tool_call in final_tool_calls.values():
                        tool_name = tool_call.function.name
                        tool_args = tool_call.function.arguments

                        result = eval(tool_name)(tool_args)

                        self.messages.append({"role": "tool", "content": str(result), "tool_call_id": tool_call.id})

                    final_tool_calls = {}

                else: response_completed = True



        self.messages.append({"role": "assistant", "content": response_message})