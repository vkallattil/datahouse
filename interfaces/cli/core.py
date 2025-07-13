import os
from prompt_toolkit import prompt
from interfaces.cli.commands import (
    registry, CommandClear, StringResponse, Response
)
from agents.core import DatahouseAgent

datahouse_agent = DatahouseAgent()

def handle_input(user_input: str) -> Response:
    if not user_input:
        return StringResponse("")
        
    if user_input.startswith('/'):
        parts = user_input[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        response = registry.execute(command, args)
        if response is not None:
            return response
            
        return StringResponse(f"Unknown command: {command}")
    
    try:
        response = datahouse_agent.process(user_input)
        return StringResponse(response)
    except Exception as e:
        return StringResponse(f"Error generating CLI response: {str(e)}")

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

            response = handle_input(user_input)

            print("\n" + response.to_string() + "\n")
            
        except CommandClear:
            os.system('cls' if os.name == 'nt' else 'clear')
            datahouse_agent.clear_messages()
            display_initial_prompt()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Type '/help' for assistance.")