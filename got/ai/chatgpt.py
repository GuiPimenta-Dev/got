import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from got.ai import AI
from got.printer import Printer

load_dotenv()
printer = Printer()


class ChatGPT(AI):
    def __init__(self, model) -> None:
        self.model = model
        self.messages = []
        CHAT_GPT_TOKEN = os.getenv("CHAT_GPT_TOKEN")
        if not CHAT_GPT_TOKEN:
            raise ValueError("CHAT_GPT_TOKEN is not set in the environment variables")
        self.client = OpenAI(api_key=CHAT_GPT_TOKEN)

    def add_message(self, content: str, role: str = "user") -> None:
        if isinstance(content, dict) or isinstance(content, list):
            content = json.dumps(content)
        message = {"role": role, "content": content}
        self.messages.append(message)

    def prompt(self) -> str:
        printer.start_spinner("Creating commit messages...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        json_content = json.loads(content)
        printer.stop_spinner()
        return json_content
