from ai import AI
from ai.chatgpt import ChatGPT


class AIFactory:
    def create_ai(self) -> AI:
        return ChatGPT("gpt-3.5-turbo")
