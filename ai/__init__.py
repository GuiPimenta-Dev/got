from abc import ABC, abstractmethod


class AI(ABC):
    @abstractmethod
    def prompt(self, prompt: str) -> str:
        pass

    @abstractmethod
    def add_message(self, content: str, role: str = "user") -> None:
        pass
