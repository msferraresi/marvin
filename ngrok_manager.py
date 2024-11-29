import os
import subprocess
import requests
import signal
import logging

logger = logging.getLogger(__name__)


class NgrokManager:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.ngrok_process = None
        self.ngrok_url = None

    def run_ngrok(self, port):
        ngrok_path = os.path.join(os.getcwd(), "resources", "ngrok.exe")

        if not os.path.exists(ngrok_path):
            logger.error(f"No se encontró ngrok en {ngrok_path}")
            raise FileNotFoundError(f"No se encontró ngrok en {ngrok_path}")

        self.ngrok_process = subprocess.Popen(
            [ngrok_path, "http", f"127.0.0.1:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("ngrok está corriendo...")

    def get_public_url(self):
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels")
            tunnels_info = response.json()
            self.ngrok_url = tunnels_info["tunnels"][0]["public_url"]
            logger.info(f"ngrok URL pública: {self.ngrok_url}")
            return self.ngrok_url
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener la URL pública de ngrok: {e}")
            return None

    def set_telegram_webhook(self, ngrok_url):
        webhook_url = f"https://api.telegram.org/bot{self.bot_token}/setWebhook?url={ngrok_url}/bot/"
        try:
            response = requests.get(webhook_url)
            if response.status_code == 200:
                logger.info("Webhook configurado correctamente en Telegram.")
            else:
                logger.error(f"Error al configurar el webhook: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al hacer la petición al webhook de Telegram: {e}")

    def stop_ngrok(self):
        if self.ngrok_process:
            self.ngrok_process.send_signal(signal.SIGTERM)
            self.ngrok_process.wait()
            logger.info("ngrok ha sido detenido.")
