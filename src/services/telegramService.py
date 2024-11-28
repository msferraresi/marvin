from flask import Blueprint, request

from src.controllers import AssistantController
from src.controllers.telegramController import TelegramController
from src.interfaces.chat_gpt import ChatGPT
from src.interfaces.gemini import Gemini


app = Blueprint("bot", __name__, url_prefix="/bot")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        assistants = [ChatGPT(), Gemini()]
        assistant_manager = AssistantController(assistants)
        return TelegramController(data, assistant_manager).process_data()

    return "<h1>Hola Comunidad</h1>"
