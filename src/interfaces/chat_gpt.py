import openai
from flask import current_app
import time
from openai.error import RateLimitError, APIError, Timeout
import logging
from src.interfaces.iassistant import IAssistant

logger = logging.getLogger(__name__)

CHATGPT_API_KEY = current_app.config["CHATGPT_API_KEY"]


class ChatGPT(IAssistant):
    def ask_for_intent(self, text, opciones=""):
        """
        Consulta a ChatGPT para obtener la intención de un mensaje.
        """
        openai.api_key = CHATGPT_API_KEY
        prompt = f"El siguiente mensaje pertenece a una conversación de chatbot: '{text}'. ¿Cuál es la intención del mensaje?{opciones}"
        logger.debug(f"Generando prompt para intent: {prompt}")

        for retry in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"Intento {retry + 1} de {self.MAX_RETRIES} para obtener intent."
                )
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Determina la intención del usuario.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=60,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                result = response["choices"][0]["message"]["content"].strip().lower()
                logger.info(f"Respuesta recibida de ChatGPT para intent: {result}")
                return result
            except RateLimitError as e:
                logger.warning(
                    f"Rate limit alcanzado en intento {retry + 1}. Reintentando en {self.RETRY_SLEEP} segundos..."
                )
                self._handle_retry(retry, e)
            except (APIError, Timeout) as e:
                logger.error(
                    f"Error de API o timeout en intento {retry + 1}: {e}. Reintentando en {self.RETRY_SLEEP} segundos..."
                )
                self._handle_retry(retry, e)
        logger.critical(
            "No se pudo completar la solicitud para obtener intent tras múltiples intentos."
        )
        return "Error: No se pudo completar la solicitud para obtener intent."

    def ask_for_response(self, text, opciones="."):
        """
        Consulta a ChatGPT para obtener una respuesta como Marvin el robot.
        """
        openai.api_key = CHATGPT_API_KEY
        prompt = f'Responde como Marvin el robot de "La guía del viajero intergaláctico" cuando "{text}", la respuesta debe ser corta, no utilices palabras en inglés{opciones}'
        logger.debug(f"Generando prompt para respuesta: {prompt}")

        for retry in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"Intento {retry + 1} de {self.MAX_RETRIES} para obtener respuesta."
                )
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are Marvin, a sarcastic and intelligent robot.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=60,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                result = response["choices"][0]["message"]["content"].strip().lower()
                logger.info(f"Respuesta recibida de ChatGPT: {result}")
                return result
            except RateLimitError as e:
                logger.warning(
                    f"Rate limit alcanzado en intento {retry + 1}. Reintentando en {self.RETRY_SLEEP} segundos..."
                )
                self._handle_retry(retry, e)
            except (APIError, Timeout) as e:
                logger.error(
                    f"Error de API o timeout en intento {retry + 1}: {e}. Reintentando en {self.RETRY_SLEEP} segundos..."
                )
                self._handle_retry(retry, e)
        logger.critical(
            "No se pudo completar la solicitud para obtener respuesta tras múltiples intentos."
        )
        return "Error: No se pudo completar la solicitud para obtener respuesta."

    def _handle_retry(self, retry, exception):
        """
        Maneja los reintentos en caso de errores.
        """
        if retry < self.MAX_RETRIES - 1:
            logger.debug(
                f"Esperando {self.RETRY_SLEEP} segundos antes de reintentar..."
            )
            time.sleep(self.RETRY_SLEEP)
        else:
            logger.critical("Se alcanzó el número máximo de reintentos.")
            raise exception
