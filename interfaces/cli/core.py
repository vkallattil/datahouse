import os
import asyncio
import traceback
import json
from prompt_toolkit import prompt
from interfaces.cli.commands import (
    registry, CommandClear, StringResponse, Response
)
from agents.core import DatahouseAgent

datahouse_agent = DatahouseAgent()

async def handle_input(user_input: str) -> None:
    if not user_input:
        print("")
        return

    if user_input.startswith('/'):
        parts = user_input[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        response = registry.execute(command, args)
        if response is not None:
            print(response.to_string())
            return
        print(f"Unknown command: {command}")
        return
    
    async for chunk in datahouse_agent.process(user_input):
        print(chunk, end="", flush=True)
    
    print()

def display_initial_prompt() -> None:
    print("=" * 50)
    print("Type '/help' to see available commands.")
    print("Otherwise type your query.")
    print("=" * 50 + "\n")

def run_assistant_cli() -> None:
    display_initial_prompt()

    while True:
        try:
            user_input = prompt(">> ").strip()

            if not user_input:
                continue

            asyncio.run(handle_input(user_input))
            
        except CommandClear:
            os.system('cls' if os.name == 'nt' else 'clear')
            datahouse_agent.clear_messages()
            display_initial_prompt()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
