import json
from flask import current_app
import requests
import unicodedata
import logging
from src import db

from src.controllers.assistantController import AssistantController
from src.interfaces.chat_gpt import ChatGPT
from src.interfaces.gemini import Gemini
from src.models import IntentsSchema, Intents, IntentTypes, IntentTypesSchema

logger = logging.getLogger(__name__)

CHATGPT_API_KEY = current_app.config["CHATGPT_API_KEY"]

TOKEN = current_app.config["TELEGRAM_TOKEN"]
BASE_URL = current_app.config["TELEGRAM_API"].replace("[TOKEN]", TOKEN)
schemaIntents = IntentsSchema()
schemaIntentsType = IntentTypesSchema()


class TelegramController:
    def __init__(self):
        logger.debug("Inicializando TelegramController con datos recibidos.")
        self.data = None
        self.chat_id = None
        self.text = None
        self.payload_type = None
        assistants = [
            {"ia": ChatGPT(), "status": current_app.config.get("CHATGPT", False)},
            {"ia": Gemini(), "status": current_app.config.get("GEMINI", False)},
        ]
        self.assistant_manager = AssistantController(assistants)
        self.valid_intents = [
            {"id": intent_type.id, "description": intent_type.description}
            for intent_type in IntentTypes.query.with_entities(
                IntentTypes.id, IntentTypes.description
            ).all()
        ]

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

    def process_data(self, data):
        logger.debug(f"Procesando datos: {self.data}")

        self.data = data
        chat_id, text, payload_type = self.get_chat_data()
        self.chat_id = chat_id
        self.text = text
        self.payload_type = payload_type
        logger.info(
            f"Datos del chat extraídos: chat_id={chat_id}, text={text}, payload_type={payload_type}"
        )

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
            self.handle_unknown_payload(self.chat_id, self.text)
        return self.data

    # ---------------------------------------------------HANDLERS PAYLOAD TYPE
    def handle_text_payload(self, chat_id):
        logger.debug("Procesando payload de tipo texto.")
        text = self.text.strip()
        text = text.replace("/", "").replace("\\", "")
        result = ""

        if filtered_text := self.remove_emojis(text).strip():
            logger.info(f"Texto filtrado: {filtered_text}")

            # Buscar intent conocido en la base de datos
            if intent := Intents.query.filter_by(keyword=filtered_text).first():
                logger.info(
                    f"Intención encontrada en la base de datos: {intent.intent_type.description}"
                )
                result = self.handle_known_intent(
                    intent.intent_type.description, chat_id, filtered_text
                )
            else:
                logger.warning(
                    "Intención no encontrada en la base de datos, intentando identificarla con la IA."
                )

                # Obtener intent válido desde IA
                intent_descriptions = [
                    intent["description"] for intent in self.valid_intents
                ]
                intent = self.assistant_manager.get_intent(
                    filtered_text,
                    f" Entre las siguientes: {', '.join(intent_descriptions)}, other. Responde solo con las opciones dadas",
                )
                logger.info(f"Respuesta de IA: {intent}")
                # Validar si el intent está en las descripciones válidas
                if intent.strip().lower() in intent_descriptions:
                    try:
                        # Guardar nuevo intent en la base de datos
                        self.save_intent_to_db(intent.strip().lower(), filtered_text)
                        result = self.handle_known_intent(
                            intent.strip().lower(), chat_id, filtered_text
                        )
                    except Exception as e:
                        logger.error(
                            f"Error guardando el intent en la base de datos: {e}"
                        )
                        self.handle_unknown_payload(chat_id, filtered_text)
                else:
                    logger.warning(
                        f"La IA no identificó una intención clara: {filtered_text}"
                    )
                    self.handle_unknown_payload(chat_id, filtered_text)
        else:
            logger.warning("El texto contiene solo emojis o caracteres irreconocibles.")
            self.send_text_message(
                chat_id,
                "Recibido solo un emoji.\nAún no sé qué hacer con este tipo de mensaje.",
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

    # ---------------------------------------------------HANDLERS PAYLOAD
    def handle_unknown_payload(self, chat_id, text=None):
        logger.warning("Procesando payload desconocido.")
        try:
            intent = "la intención es desconocida"
            if len(text) > 0:
                intent += f" y el texto es: {text}"
            rta = self.assistant_manager.get_response(intent)
            logger.info("Respuesta obtenida de la IA.")
        except Exception as e:
            logger.error(f"Error al procesar con la IA: {e}")
            rta = "Lo siento, en este momento no puedo procesar tu solicitud."
        return self.send_text_message(chat_id, rta)

    def handle_known_intent(self, intent, chat_id, text):
        logger.info(f"Procesando intención conocida: {intent}")
        intent_handlers = {
            "greeting": self.handle_greeting,
            "farewell": self.handle_farewell,
            "help": self.handle_help,
            "information": self.handle_information,
            "register": self.handle_register,
        }

        if handler := intent_handlers.get(intent):
            return handler(chat_id)
        else:
            logger.warning(f"Intención no manejada: {intent}")
            self.handle_unknown_payload(chat_id, text)

    # ---------------------------------------------------HANDLERS RESPONSES TYPE
    def handle_greeting(self, chat_id):
        logger.info("Enviando mensaje de saludo.")
        return self.send_text_message(chat_id, "¡Hola! ¿Cómo estás?")

    def handle_farewell(self, chat_id):
        logger.info("Enviando mensaje de despedida.")
        return self.send_text_message(chat_id, "¡Adiós! Hasta luego.")

    def handle_help(self, chat_id):
        logger.info("Enviando mensaje de ayuda.")
        help_message = """
            Los comandos que puedes ejecutar son los siguientes:

            - *saludos*: Te permite enviar un saludo.
            - *despedidas*: Te permite enviar una despedida.
            - *ayudas*: Te muestra este mensaje de ayuda con los comandos disponibles.

            Escribe cualquiera de estos comandos para interactuar conmigo.
            """
        return self.send_text_message(chat_id, help_message)

    def handle_information(self, chat_id):
        logger.info("request_credentials_template")
        return self.request_credentials_template(chat_id)

    def handle_register(self, chat_id):
        logger.info("Enviando mensaje de saludo.")
        return self.send_text_message(chat_id, "¡Hola! ¿Cómo estás?")

    # ---------------------------------------------------ACTIONS

    def request_credentials_template(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [{"text": "Ingresar Usuario", "callback_data": "enter_username"}],
                [{"text": "Ingresar Contraseña", "callback_data": "enter_password"}],
            ]
        }
        return self.send_text_message2(
            chat_id,
            "Por favor, ingresa tus credenciales de Redmine usando los botones:",
            reply_markup=keyboard,
        )

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

    def send_text_message2(self, chat_id, text, reply_markup=None):
        """
        Envía un mensaje de texto a un usuario de Telegram.

        Args:
            chat_id (int): ID del chat de Telegram al que se envía el mensaje.
            text (str): El texto del mensaje a enviar.
            reply_markup (dict, optional): Teclado u opciones adicionales para el mensaje.
        Returns:
            Response: Respuesta HTTP de la API de Telegram.
        """
        url = f"{BASE_URL}sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Mensaje enviado a chat_id={chat_id}: {text}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar mensaje a chat_id={chat_id}: {e}")
            raise

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

    # ---------------------------------------------------UTILS
    def remove_emojis(self, text):
        logger.debug("Eliminando emojis del texto.")
        return "".join(
            char for char in text if not unicodedata.category(char).startswith("So")
        )

    def save_intent_to_db(self, intent_type, keyword):
        """Guarda un intent en la base de datos."""
        try:
            logger.debug(f"Intent Type: {intent_type}, Keyword: {keyword}")

            # Obtiene el ID del intent_type a partir de la descripción
            intent_type_obj = IntentTypes.query.filter_by(
                description=intent_type
            ).first()
            if not intent_type_obj:
                raise ValueError(
                    f"El intent_type '{intent_type}' no existe en la base de datos."
                )

            # Crea y guarda el nuevo intent
            new_intent = Intents(intent_type_id=intent_type_obj.id, keyword=keyword)
            db.session.add(new_intent)
            db.session.commit()
            logger.info(f"Intent '{intent_type}' guardado en la base de datos.")
        except Exception as e:
            db.session.rollback()  # Limpia la sesión en caso de error
            logger.error(f"Error guardando el intent en la base de datos: {e}")
