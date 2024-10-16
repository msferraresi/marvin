import json
from pprint import pprint
from flask import current_app
import requests
import unicodedata

from src.controllers.chatGPTController import ChatGPTController
from src.controllers.geminiController import GeminiController

from src.models import IntentsSchema, Intents

CHATGPT_API_KEY = current_app.config["CHATGPT_API_KEY"]

TOKEN = current_app.config["TELEGRAM_TOKEN"]
BASE_URL = current_app.config["TELEGRAM_API"].replace("[TOKEN]", TOKEN)
schemaIntents = IntentsSchema()


class TelegramController:
    def __init__(self, data):
        self.data = data
        chat_id, text, payload_type = self.get_chat_data()
        self.chat_id = chat_id
        self.text = text
        self.payload_type = payload_type

    def get_chat_data(self):
        if message_data := self.data.get("message") or self.data.get("edited_message"):
            chat_id = message_data.get("chat", {}).get("id")
            text = message_data.get("text")
            payload_type = list(message_data.keys())[-1]
            return chat_id, text, payload_type
        return None, None, None

    def process_data(self):
        # print(
        #     ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        # )
        # print(f"MENSAJE:")
        # pprint(self.data)
        # print(
        #     "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        # )

        if not self.chat_id:
            raise ValueError("No se pudo obtener el chat_id del mensaje.")

        if handler_payload_type := {
            "text": self.handle_text_payload,
            "photo": self.handle_photo_payload,
            "voice": self.handle_voice_payload,
            "sticker": self.handle_sticker_payload,
            "document": self.handle_document_payload,
        }.get(self.payload_type):
            handler_payload_type(self.chat_id)
        else:
            self.handle_unknown_payload(self.chat_id)
        return self.data

    def handle_known_intent(self, intent, chat_id):
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # print(f"handle_known_intent>INTENT: {intent}")
        # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        intent_handlers = {
            "greeting": self.handle_text_greeting,
            "farewell": self.handle_text_farewell,
            "help": self.handle_text_help,
        }

        if handler := intent_handlers.get(intent):
            return handler(chat_id)
        else:
            self.handle_unknown_payload(chat_id)

    # ---------------------------------------------------HANDLERS PAYLOAD TYPE
    def handle_text_payload(self, chat_id):
        text = self.text.strip()
        text = text.replace("/", "").replace("\\", "")
        result = ""
        # Filtrar emojis y espacios en blanco
        if filtered_text := self.remove_emojis(text).strip():
            # Buscar intent en la base de datos
            if intent := Intents.query.filter_by(keyword=filtered_text).first():
                result = self.handle_known_intent(intent.intent_type, chat_id)
            else:
                # Intentar identificar la intención con Gemini
                intent = GeminiController.ask_gemini_for_intent(
                    filtered_text,
                    " Entre las siguientes: greeting, farewell, help, other. Responde solo con las opciones dadas",
                )
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                # print(f"INTENT: {intent}")
                # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                # # Si no se pudo identificar con Gemini, intentar con ChatGPT
                if intent.strip() in ["greeting", "farewell", "help"]:
                    result = self.handle_known_intent(intent.strip(), chat_id)
                else:
                    # Intentar con ChatGPT si Gemini no da un resultado claro
                    # intent = ChatGPTController.ask_chatgpt_for_intent(filtered_text)

                    # if intent in ["greeting", "farewell", "help"]:
                    #     result = self.handle_known_intent(intent, chat_id)
                    # else:
                    # Si no se identifica ninguna intención conocida, manejarlo como desconocido
                    self.handle_unknown_payload(chat_id)
        else:
            # Caso donde el mensaje contiene solo emojis o texto irreconocible
            self.send_text_message(
                chat_id,
                "Recibido solo un emoji.\nAun no se que hacer con este tipo de mensaje",
            )

        return result

    def handle_photo_payload(self, chat_id):
        return self.send_text_message(
            chat_id,
            "Recibido una imagen.\nAun no se que hacer con este tipo de mensaje",
        )

    def handle_voice_payload(self, chat_id):
        return self.send_text_message(
            chat_id,
            "Recibido un mensaje de voz.\nAun no se que hacer con este tipo de mensaje",
        )

    def handle_sticker_payload(self, chat_id):
        return self.send_text_message(
            chat_id,
            "Recibido un sticker.\nAun no se que hacer con este tipo de mensaje",
        )

    def handle_document_payload(self, chat_id):
        return self.send_text_message(
            chat_id,
            "Recibido un documento.\nAun no se que hacer con este tipo de mensaje",
        )

    def handle_unknown_payload(self, chat_id):
        try:
            # Intentamos con ChatGPT
            # rta = ChatGPTController.ask_chatgpt_for_response(
            #     "la intención es desconocida"
            # )
            rta = GeminiController.ask_gemini_for_response(
                "la intención es desconocida"
            )
        except Exception as e:
            print(f"Error con ChatGPT: {e}")
            try:
                # Si ChatGPT falla, intentamos con Google Generative AI
                rta = GeminiController.ask_gemini_for_response(
                    "la intención es desconocida"
                )
            except Exception as google_error:
                print(f"Error con Google Generative AI: {google_error}")
                rta = "Lo siento, en este momento no puedo procesar tu solicitud con ninguno de los servicios disponibles."

        return self.send_text_message(chat_id, rta)

    # ---------------------------------------------------HANDLERS TEXT TYPE
    def handle_text_greeting(self, chat_id):
        return self.send_text_message(chat_id, "¡Hola! ¿Cómo estás?")

    def handle_text_farewell(self, chat_id):
        return self.send_text_message(chat_id, "¡Adiós! Hasta luego.")

    def handle_text_help(self, chat_id):
        return self.send_text_message(chat_id, "Esto es un mensaje de ayuda.")

    # ---------------------------------------------------ACTIONS
    def send_text_message(self, chat_id, text):
        url = f"{BASE_URL}sendMessage"
        if chat_id is None or text is None:
            raise ValueError("chat_id and text are required")
        payload = {"chat_id": chat_id, "text": text}
        return requests.post(url, json=payload)

    def send_poll_message(
        self,
        chat_id,
        text,
        options,
        is_anonymous=False,
        type_poll="quiz",
        correct_opt_poll=0,
    ):
        url = f"{BASE_URL}sendPoll"
        if chat_id is None or text is None or options is None:
            raise ValueError("chat_id, text, and options are required")
        payload = {
            "chat_id": chat_id,
            "question": text,
            "options": json.dumps(options),
            "is_anonymous": is_anonymous,
            "type": type_poll,
            "correct_option_id": correct_opt_poll,
        }
        return requests.post(url, json=payload)

    def send_inlineurl_message(
        self, chat_id, lst_url, text="Cual enlace te gustaría visitar?"
    ):
        url = f"{BASE_URL}sendMessage"
        if chat_id is None or lst_url is None:
            raise ValueError("chat_id and lst_url are required")

        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "YT channel",
                            "url": "https://www.youtube.com/@rmblockcode",
                        },
                        {
                            "text": "Instagram",
                            "url": "https://www.instagram.com/rmblockcode",
                        },
                    ]
                ]
            },
        }

        return requests.post(url, json=payload)

    def send_image_message(self, chat_id, photo, caption="This is a sample image"):
        url = f"{BASE_URL}sendPhoto"
        if chat_id is None or photo is None:
            raise ValueError("chat_id and photo are required")

        payload = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
        }
        return requests.post(url, json=payload)

    def send_audio_message(self, chat_id, audio):
        url = f"{BASE_URL}sendAudio"
        if chat_id is None or audio is None:
            raise ValueError("chat_id and audio are required")

        payload = {
            "chat_id": chat_id,
            "audio": audio,
        }
        return requests.post(url, json=payload)

    def remove_emojis(self, text):
        return "".join(
            char for char in text if not unicodedata.category(char).startswith("So")
        )
