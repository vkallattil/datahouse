from openai import OpenAI
import logging
from typing import Literal
from datetime import datetime
from modules.search import search_and_read
import json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Instructions:
Respond to the user as if you are a helpful assistant.
"""

class DatahouseAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [{"role": "developer", "content": SYSTEM_PROMPT}]
        self.tools = [{
            "type": "function",
            "function": {
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
            }
        }]
    
    def clear_messages(self) -> None:
        self.messages = [{"role": "developer", "content": SYSTEM_PROMPT}]

    def process(self, message: str) -> str:
        self.messages.append({"role": "user", "content": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}"})
                
        while True:
            completion = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=self.messages,
                tools=self.tools,
            )

            if (completion.choices[0].message.tool_calls != None and completion.choices[0].message.tool_calls != []):
                self.messages.append(completion.choices[0].message)
                
                for tool_call in completion.choices[0].message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    function_name = tool_call.function.name

                    print("Calling tool: ", function_name, " with arguments: ", args)

                    result = eval(function_name)(**args)

                    self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
            
            elif (completion.choices[0].message.content != None):
                self.messages.append(completion.choices[0].message)
                break

        return self.messages[-1].content