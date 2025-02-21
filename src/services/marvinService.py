from flask import Blueprint, request

from src.controllers.telegramController import TelegramController
import logging

logger = logging.getLogger(__name__)

app = Blueprint("bot", __name__, url_prefix="/bot")
telegram = TelegramController()


@app.route("/", methods=["GET", "POST"])
def index():
    logger.info(f"Request method: {request.method}")
    if request.method == "POST":
        data = request.get_json()

        return telegram.process_data(data)

    return "<h1>Bot Activo</h1>"
