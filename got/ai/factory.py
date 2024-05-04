

from got.ai import AI
from got.ai.chatgpt import ChatGPT


class AIFactory:
    def create_ai(self) -> AI:
        return ChatGPT("gpt-3.5-turbo")
