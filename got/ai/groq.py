import json
import os

from dotenv import load_dotenv
from groq import Groq

from got.ai import AI
from got.printer import Printer

load_dotenv()
printer = Printer()


class GroqCloud(AI):
    def __init__(self, model) -> None:
        self.model = model
        self.messages = []
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in the environment variables")
        self.client = Groq(api_key=GROQ_API_KEY)

    def add_message(self, content: str, role: str = "user") -> None:
        if isinstance(content, dict) or isinstance(content, list):
            content = json.dumps(content)
        message = {"role": role, "content": content}
        self.messages.append(message)

    def prompt(self) -> str:
        printer.start_spinner("Creating commit messages...")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=1,
            max_tokens=8192,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )
        content = completion.choices[0].message.content
        json_content = json.loads(content)
        printer.stop_spinner()
        return json_content
