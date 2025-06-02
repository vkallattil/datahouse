from openai import OpenAI, OpenAIError
from utilities.env import OPENAI_API_KEY

class OpenAIChatContextManager:
    """
    Encapsulates OpenAI chat context and API interaction.
    """
    def __init__(self, system_prompt: str):
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in environment variables.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = system_prompt
        self.messages = [
            {"role": "developer", "content": system_prompt}
        ]

    def clear_messages(self):
        self.messages = [
            {"role": "developer", "content": self.system_prompt}
        ]

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def get_response(self) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=self.messages
            )
            message_content = response.choices[0].message.content
            self._add_assistant_message(message_content)
            return message_content
        except OpenAIError as e:
            raise OpenAIError(f"Error generating response: {str(e)}")
