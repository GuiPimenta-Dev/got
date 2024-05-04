import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from ai import AI

load_dotenv()

CHAT_GPT_TOKEN = os.getenv("CHAT_GPT_TOKEN")

client = OpenAI(api_key=CHAT_GPT_TOKEN)


class ChatGPT(AI):
    
    def __init__(self, model) -> None:
        self.model = model
        self.messages = []
    
    def add_message(self, content: str, role: str = "user") -> None:
        if isinstance(content, dict) or isinstance(content, list):
            content = json.dumps(content)
        message = {"role": role, "content": content}
        self.messages.append(message)
    
    def prompt(self) -> str:
        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        json_content = json.loads(content)
        return json_content