from typing import List

from src.interfaces.iassistant import IAssistant


class AssistantController:
    def __init__(self, assistants: List[IAssistant]):
        self.assistants = assistants

    def get_response(self, message: str, options="") -> str:
        for assistant in self.assistants:
            try:
                return assistant.ask_for_response(message, options)
            except Exception as e:
                print(f"Error con {assistant.__class__.__name__}: {e}")
        raise Exception("Ningún asistente está disponible actualmente.")

    def get_intent(self, message: str, options=".") -> str:
        for assistant in self.assistants:
            try:
                return assistant.ask_for_intent(message, options)
            except Exception as e:
                print(f"Error con {assistant.__class__.__name__}: {e}")
        raise Exception("No se pudo determinar la intención con ningún asistente.")
