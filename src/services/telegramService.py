from flask import Blueprint, request

from src.controllers.telegramController import TelegramController


app = Blueprint("bot", __name__, url_prefix="/bot")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        return TelegramController(data).process_data()

    return "<h1>Hola Comunidad</h1>"
