import google.generativeai as gemini
from flask import current_app
import time
import logging

GEMINI_API_KEY = current_app.config["GEMINI_API_KEY"]


class GeminiController:
    MAX_RETRIES = 3
    RETRY_SLEEP = 1

    @classmethod
    def ask_gemini_for_intent(cls, text, opciones=""):
        gemini_api_key = GEMINI_API_KEY
        gemini.configure(api_key=gemini_api_key)

        prompt = f"El siguiente mensaje pertenece a una conversación de chatbot: '{text}'. ¿Cuál es la intención del mensaje?{opciones}"
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # print(f"PROMPT: {prompt}")
        # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        for attempt in range(cls.MAX_RETRIES):
            try:
                model = gemini.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                logging.error(
                    f"Error en intento {attempt + 1} al consultar Google Generative AI para intents: {e}"
                )
                if attempt < cls.MAX_RETRIES - 1:
                    time.sleep(cls.RETRY_SLEEP)  # Esperamos antes de reintentar
                else:
                    return "Error: No se pudo completar la solicitud a Google Generative AI para intents."

    @classmethod
    def ask_gemini_for_response(cls, text, opciones="."):
        gemini_api_key = GEMINI_API_KEY

        gemini.configure(api_key=gemini_api_key)

        prompt = f'Responde como Marvin el robot de "La guía del viajero intergaláctico" cuando "{text}", la respuesta debe ser corta, no utilices palabras en inglés{opciones}'

        for attempt in range(cls.MAX_RETRIES):
            try:
                model = gemini.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text

            except Exception as e:
                logging.error(
                    f"Error en intento {attempt + 1} al consultar Google Generative AI: {e}"
                )
                if attempt < cls.MAX_RETRIES - 1:
                    time.sleep(cls.RETRY_SLEEP)  # Esperamos antes de reintentar
                else:
                    return "Error: No se pudo completar la solicitud a Google Generative AI."
