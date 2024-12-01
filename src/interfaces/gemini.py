import google.generativeai as gemini
from flask import current_app
import time
import logging

from src.interfaces.iassistant import IAssistant

logger = logging.getLogger(__name__)

GEMINI_API_KEY = current_app.config["GEMINI_API_KEY"]


class Gemini(IAssistant):

    def ask_for_intent(self, text, opciones=""):
        """
        Método para consultar Google Generative AI y obtener la intención de un mensaje.
        """
        gemini_api_key = GEMINI_API_KEY
        gemini.configure(api_key=gemini_api_key)

        prompt = f"El siguiente mensaje pertenece a una conversación de chatbot: '{text}'. ¿Cuál es la intención del mensaje?{opciones}"
        logger.debug(f"Generando prompt para intent: {prompt}")

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"Intento {attempt + 1} de {self.MAX_RETRIES} para obtener intent."
                )
                model = gemini.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                logger.info("Respuesta recibida de Google Generative AI para intent.")
                return response.text

            except Exception as e:
                logger.error(
                    f"Error en intento {attempt + 1} al consultar Google Generative AI para intents: {e}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    logger.debug(f"Reintentando en {self.RETRY_SLEEP} segundos...")
                    time.sleep(self.RETRY_SLEEP)  # Esperamos antes de reintentar
                else:
                    logger.critical(
                        "No se pudo completar la solicitud a Google Generative AI para intents tras múltiples intentos."
                    )
                    return "Error: No se pudo completar la solicitud a Google Generative AI para intents."

    def ask_for_response(self, text, opciones="."):
        """
        Método para consultar Google Generative AI y obtener una respuesta como Marvin el robot.
        """
        gemini_api_key = GEMINI_API_KEY
        gemini.configure(api_key=gemini_api_key)

        prompt = f'Responde como Marvin el robot de "La guía del viajero intergaláctico" cuando "{text}", la respuesta debe ser corta, no utilices palabras en inglés{opciones}'
        logger.debug(f"Generando prompt para respuesta: {prompt}")

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"Intento {attempt + 1} de {self.MAX_RETRIES} para obtener respuesta."
                )
                model = gemini.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                logger.info("Respuesta recibida de Google Generative AI.")
                return response.text

            except Exception as e:
                logger.error(
                    f"Error en intento {attempt + 1} al consultar Google Generative AI: {e}"
                )
                if attempt < self.MAX_RETRIES - 1:
                    logger.debug(f"Reintentando en {self.RETRY_SLEEP} segundos...")
                    time.sleep(self.RETRY_SLEEP)  # Esperamos antes de reintentar
                else:
                    logger.critical(
                        "No se pudo completar la solicitud a Google Generative AI tras múltiples intentos."
                    )
                    return "Error: No se pudo completar la solicitud a Google Generative AI."
