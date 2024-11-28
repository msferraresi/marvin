import openai
from flask import current_app
import time
from openai.error import RateLimitError, APIError, Timeout
import logging

CHATGPT_API_KEY = current_app.config["CHATGPT_API_KEY"]


class ChatGPTController_OLD:
    MAX_RETRIES = 3
    RETRY_SLEEP = 1

    @classmethod
    def ask_chatgpt_for_intent(cls, text, opciones=""):
        openai.api_key = CHATGPT_API_KEY
        prompt = f"El siguiente mensaje pertenece a una conversación de chatbot: '{text}'. ¿Cuál es la intención del mensaje?{opciones}"

        for retry in range(cls.MAX_RETRIES):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": ""},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=60,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                return response["choices"][0]["message"]["content"].strip().lower()
            except RateLimitError as e:
                if retry < cls.MAX_RETRIES - 1:
                    logging.error(
                        f"Rate limit alcanzado. Reintentando en {cls.RETRY_SLEEP} segundos..."
                    )
                    time.sleep(cls.RETRY_SLEEP)
                else:
                    logging.error(
                        "Se alcanzó el número máximo de reintentos por rate limit."
                    )
                    raise e
            except (APIError, Timeout) as e:
                if retry < cls.MAX_RETRIES - 1:
                    logging.error(
                        f"Error de API o timeout. Reintentando en {cls.RETRY_SLEEP} segundos..."
                    )
                    time.sleep(cls.RETRY_SLEEP)
                else:
                    logging.error(
                        "Se alcanzó el número máximo de reintentos por error de API o timeout."
                    )
                    raise e

    @classmethod
    def ask_chatgpt_for_response(cls, text, opciones="."):
        openai.api_key = CHATGPT_API_KEY
        prompt = f'Responde como Marvin el robot de "La guía del viajero intergaláctico" cuando "{text}", la respuesta debe ser corta, no utilices palabras en inglés{opciones}'

        for retry in range(cls.MAX_RETRIES):
            try:
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
                return response["choices"][0]["message"]["content"].strip().lower()
            except RateLimitError as e:
                if retry < cls.MAX_RETRIES - 1:
                    logging.error(
                        f"Rate limit alcanzado. Reintentando en {cls.RETRY_SLEEP} segundos..."
                    )
                    time.sleep(cls.RETRY_SLEEP)
                else:
                    logging.error(
                        "Se alcanzó el número máximo de reintentos por rate limit."
                    )
                    raise e
            except (APIError, Timeout) as e:
                if retry < cls.MAX_RETRIES - 1:
                    logging.error(
                        f"Error de API o timeout. Reintentando en {cls.RETRY_SLEEP} segundos..."
                    )
                    time.sleep(cls.RETRY_SLEEP)
                else:
                    logging.error(
                        "Se alcanzó el número máximo de reintentos por error de API o timeout."
                    )
                    raise e
