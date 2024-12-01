from abc import ABC, abstractmethod


class IAssistant(ABC):
    MAX_RETRIES = 3
    RETRY_SLEEP = 1

    @abstractmethod
    def ask_for_response(self, text, opciones="") -> str:
        pass

    @abstractmethod
    def ask_for_intent(self, text, opciones=".") -> str:
        pass
