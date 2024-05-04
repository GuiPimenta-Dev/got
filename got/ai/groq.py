import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from got.ai import AI
from got.printer import Printer

load_dotenv()
printer = Printer()
GROQ_TOKEN = os.getenv("GROQ_TOKEN")

client = OpenAI(api_key=GROQ_TOKEN)


class Groq(AI):
    def __init__(self, model) -> None:
        self.model = model
        self.messages = []

    def add_message(self, content: str, role: str = "user") -> None:
        if isinstance(content, dict) or isinstance(content, list):
            content = json.dumps(content)
        message = {"role": role, "content": content}
        self.messages.append(message)

    def prompt(self) -> str:
        printer.start_spinner("Creating commit messages...")
        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        json_content = json.loads(content)
        printer.stop_spinner()
        return json_content
