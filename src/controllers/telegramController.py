import json
from pprint import pprint
from flask import current_app
import requests
import unicodedata
import logging


from src.controllers.chatGPTController import ChatGPTController
from src.controllers.geminiController import GeminiController

from src.models import IntentsSchema, Intents

logger = logging.getLogger(__name__)

CHATGPT_API_KEY = current_app.config["CHATGPT_API_KEY"]

TOKEN = current_app.config["TELEGRAM_TOKEN"]
BASE_URL = current_app.config["TELEGRAM_API"].replace("[TOKEN]", TOKEN)
schemaIntents = IntentsSchema()


class TelegramController:
    def __init__(self, data):
        logger.debug("Inicializando TelegramController con datos recibidos.")
        self.data = data
        chat_id, text, payload_type = self.get_chat_data()
        self.chat_id = chat_id
        self.text = text
        self.payload_type = payload_type
        logger.info(
            f"Datos del chat extraídos: chat_id={chat_id}, text={text}, payload_type={payload_type}"
        )

    def get_chat_data(self):
        logger.debug("Extrayendo datos del mensaje...")
        if message_data := self.data.get("message") or self.data.get("edited_message"):
            chat_id = message_data.get("chat", {}).get("id")
            text = message_data.get("text")
            payload_type = list(message_data.keys())[-1]
            logger.info("Datos extraídos exitosamente del mensaje.")
            return chat_id, text, payload_type
        logger.warning("No se encontraron datos válidos en el mensaje.")
        return None, None, None

    def process_data(self):
        logger.debug(f"Procesando datos: {self.data}")

        if not self.chat_id:
            logger.error("No se pudo obtener el chat_id del mensaje.")
            raise ValueError("No se pudo obtener el chat_id del mensaje.")

        logger.info(f"Procesando payload_type: {self.payload_type}")
        if handler_payload_type := {
            "text": self.handle_text_payload,
            "photo": self.handle_photo_payload,
            "voice": self.handle_voice_payload,
            "sticker": self.handle_sticker_payload,
            "document": self.handle_document_payload,
        }.get(self.payload_type):
            handler_payload_type(self.chat_id)
        else:
            logger.warning(f"Tipo de payload desconocido: {self.payload_type}")
            self.handle_unknown_payload(self.chat_id)
        return self.data

    def handle_known_intent(self, intent, chat_id):
        logger.info(f"Procesando intención conocida: {intent}")
        intent_handlers = {
            "greeting": self.handle_text_greeting,
            "farewell": self.handle_text_farewell,
            "help": self.handle_text_help,
        }

        if handler := intent_handlers.get(intent):
            return handler(chat_id)
        else:
            logger.warning(f"Intención no manejada: {intent}")
            self.handle_unknown_payload(chat_id)

    # ---------------------------------------------------HANDLERS PAYLOAD TYPE
    def handle_text_payload(self, chat_id):
        logger.debug("Procesando payload de tipo texto.")
        text = self.text.strip()
        text = text.replace("/", "").replace("\\", "")
        result = ""
        if filtered_text := self.remove_emojis(text).strip():
            logger.info(f"Texto filtrado: {filtered_text}")
            if intent := Intents.query.filter_by(keyword=filtered_text).first():
                logger.info(
                    f"Intención encontrada en la base de datos: {intent.intent_type}"
                )
                result = self.handle_known_intent(intent.intent_type, chat_id)
            else:
                logger.warning(
                    "Intención no encontrada en la base de datos, intentando identificarla con Gemini."
                )
                intent = GeminiController.ask_gemini_for_intent(
                    filtered_text,
                    "Entre las siguientes: greeting, farewell, help, other. Responde solo con las opciones dadas",
                )
                logger.info(f"Respuesta de Gemini: {intent}")
                if intent.strip() in ["greeting", "farewell", "help"]:
                    result = self.handle_known_intent(intent.strip(), chat_id)
                else:
                    logger.warning("Gemini no identificó una intención clara.")
                    self.handle_unknown_payload(chat_id)
        else:
            logger.warning("El texto contiene solo emojis o caracteres irreconocibles.")
            self.send_text_message(
                chat_id,
                "Recibido solo un emoji.\nAún no sé qué hacer con este tipo de mensaje",
            )

        return result

    def handle_photo_payload(self, chat_id):
        logger.debug("Procesando payload de tipo imagen.")
        return self.send_text_message(
            chat_id,
            "Recibido una imagen.\nAún no sé qué hacer con este tipo de mensaje",
        )

    def handle_voice_payload(self, chat_id):
        logger.debug("Procesando payload de tipo mensaje de voz.")
        return self.send_text_message(
            chat_id,
            "Recibido un mensaje de voz.\nAún no sé qué hacer con este tipo de mensaje",
        )

    def handle_sticker_payload(self, chat_id):
        logger.debug("Procesando payload de tipo sticker.")
        return self.send_text_message(
            chat_id,
            "Recibido un sticker.\nAún no sé qué hacer con este tipo de mensaje",
        )

    def handle_document_payload(self, chat_id):
        logger.debug("Procesando payload de tipo documento.")
        return self.send_text_message(
            chat_id,
            "Recibido un documento.\nAún no sé qué hacer con este tipo de mensaje",
        )

    # def handle_unknown_payload(self, chat_id):
    #     try:
    #         # Intentamos con ChatGPT
    #         # rta = ChatGPTController.ask_chatgpt_for_response(
    #         #     "la intención es desconocida"
    #         # )
    #         rta = GeminiController.ask_gemini_for_response(
    #             "la intención es desconocida"
    #         )
    #     except Exception as e:
    #         print(f"Error con ChatGPT: {e}")
    #         try:
    #             # Si ChatGPT falla, intentamos con Google Generative AI
    #             rta = GeminiController.ask_gemini_for_response(
    #                 "la intención es desconocida"
    #             )
    #         except Exception as google_error:
    #             print(f"Error con Google Generative AI: {google_error}")
    #             rta = "Lo siento, en este momento no puedo procesar tu solicitud con ninguno de los servicios disponibles."

    #     return self.send_text_message(chat_id, rta)
    def handle_unknown_payload(self, chat_id):
        logger.warning("Procesando payload desconocido.")
        try:
            rta = GeminiController.ask_gemini_for_response(
                "la intención es desconocida"
            )
            logger.info("Respuesta obtenida de Gemini.")
        except Exception as e:
            logger.error(f"Error al procesar con Gemini: {e}")
            rta = "Lo siento, en este momento no puedo procesar tu solicitud."
        return self.send_text_message(chat_id, rta)

    # ---------------------------------------------------HANDLERS TEXT TYPE
    def handle_text_greeting(self, chat_id):
        logger.info("Enviando mensaje de saludo.")
        return self.send_text_message(chat_id, "¡Hola! ¿Cómo estás?")

    def handle_text_farewell(self, chat_id):
        logger.info("Enviando mensaje de despedida.")
        return self.send_text_message(chat_id, "¡Adiós! Hasta luego.")

    def handle_text_help(self, chat_id):
        logger.info("Enviando mensaje de ayuda.")
        return self.send_text_message(chat_id, "Esto es un mensaje de ayuda.")

    # ---------------------------------------------------ACTIONS
    def send_text_message(self, chat_id, text):
        logger.debug(f"Enviando mensaje al chat_id={chat_id} con texto: {text}")
        url = f"{BASE_URL}sendMessage"
        if chat_id is None or text is None:
            logger.error("chat_id y texto son requeridos para enviar un mensaje.")
            raise ValueError("chat_id and text are required")
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        logger.info(f"Mensaje enviado con éxito: {response.status_code}")
        return response

    def send_poll_message(
        self,
        chat_id,
        text,
        options,
        is_anonymous=False,
        type_poll="quiz",
        correct_opt_poll=0,
    ):
        logger.debug(f"Enviando encuesta al chat_id={chat_id} con texto: {text}")
        url = f"{BASE_URL}sendPoll"
        if chat_id is None or text is None or options is None:
            logger.error(
                "chat_id, texto y opciones son requeridos para enviar una encuesta."
            )
            raise ValueError("chat_id, text, and options are required")

        payload = {
            "chat_id": chat_id,
            "question": text,
            "options": json.dumps(options),
            "is_anonymous": is_anonymous,
            "type": type_poll,
            "correct_option_id": correct_opt_poll,
        }

        response = requests.post(url, json=payload)
        logger.info(f"Encuesta enviada, status_code={response.status_code}")
        return response

    def send_inlineurl_message(
        self, chat_id, lst_url=None, text="¿Cuál enlace te gustaría visitar?"
    ):
        logger.debug(f"Enviando mensaje con URLs al chat_id={chat_id}.")
        url = f"{BASE_URL}sendMessage"
        if chat_id is None or lst_url is None:
            logger.error(
                "chat_id y lst_url son requeridos para enviar un mensaje con URLs."
            )
            raise ValueError("chat_id and lst_url are required")

        # Construir botones dinámicos desde lst_url
        inline_keyboard = [[{"text": label, "url": link} for label, link in lst_url]]

        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {"inline_keyboard": inline_keyboard},
        }

        response = requests.post(url, json=payload)
        logger.info(f"Mensaje con URLs enviado, status_code={response.status_code}")
        return response

    def send_image_message(
        self, chat_id, photo, caption="Esta es una imagen de ejemplo"
    ):
        logger.debug(f"Enviando imagen al chat_id={chat_id}.")
        url = f"{BASE_URL}sendPhoto"
        if chat_id is None or photo is None:
            logger.error("chat_id y photo son requeridos para enviar una imagen.")
            raise ValueError("chat_id and photo are required")

        payload = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
        }

        response = requests.post(url, json=payload)
        logger.info(f"Imagen enviada, status_code={response.status_code}")
        return response

    def send_audio_message(self, chat_id, audio):
        logger.debug(f"Enviando audio al chat_id={chat_id}.")
        url = f"{BASE_URL}sendAudio"
        if chat_id is None or audio is None:
            logger.error("chat_id y audio son requeridos para enviar un audio.")
            raise ValueError("chat_id and audio are required")

        payload = {
            "chat_id": chat_id,
            "audio": audio,
        }

        response = requests.post(url, json=payload)
        logger.info(f"Audio enviado, status_code={response.status_code}")
        return response

    def remove_emojis(self, text):
        logger.debug("Eliminando emojis del texto.")
        return "".join(
            char for char in text if not unicodedata.category(char).startswith("So")
        )
