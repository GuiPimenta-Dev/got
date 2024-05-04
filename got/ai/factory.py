import os
from dotenv import load_dotenv

from got.ai import AI
from got.ai.chatgpt import ChatGPT
from got.ai.groq import GroqCloud

load_dotenv()
LLM_MODEL = os.environ.get("LLM_MODEL")

OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4-turbo"]
GROQ_MODELS = ["gemma-7b-it", "llama2-70b-4096", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]


class AIFactory:

    def create_ai(self, model) -> AI:
        
        if model in OPENAI_MODELS:
            return ChatGPT(model)
        
        elif model in GROQ_MODELS:
            return GroqCloud(model)
