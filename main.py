import logging
import sys
import time
import threading
from src import create_app
from ngrok_manager import NgrokManager  # Asegúrate de tener este archivo
import signal


ngrok_manager = None
logger = logging.getLogger(__name__)


def configure_logging(minimum_detail):
    """Configura el logging según el detalle mínimo especificado."""
    logging_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    level = logging_levels.get(minimum_detail.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info(f"Logging configurado con nivel: {minimum_detail.upper()}")


def run_ngrok_and_set_webhook(bot_token, port):
    global ngrok_manager
    ngrok_manager = NgrokManager(bot_token)
    ngrok_manager.run_ngrok(port)
    time.sleep(5)

    if public_url := ngrok_manager.get_public_url():
        ngrok_manager.set_telegram_webhook(public_url)
    else:
        logger.error("No se pudo obtener la URL pública de ngrok.")


def signal_handler(sig, frame):
    global ngrok_manager
    logger.info("Cerrando la aplicación...")
    if ngrok_manager:
        ngrok_manager.stop_ngrok()
    sys.exit(0)


def main():
    global environment

    environment = "development" if len(sys.argv) == 1 else sys.argv[1]

    app = create_app(environment)

    minimum_detail = app.config.get("MINIMUN_LOGGER_DETAIL", "INFO")
    configure_logging(minimum_detail)

    bot_token = app.config.get("TELEGRAM_TOKEN")
    run_port = app.config.get("RUN_PORT")

    if not bot_token or not run_port:
        logger.error(
            "Error: TELEGRAM_TOKEN o RUN_PORT no encontrado en la configuración."
        )
        sys.exit(1)

    if environment == "development":
        ngrok_thread = threading.Thread(
            target=run_ngrok_and_set_webhook,
            args=(bot_token, run_port),
        )
        ngrok_thread.start()

    signal.signal(signal.SIGINT, signal_handler)

    # Ejecutar la app Flask en el puerto 5002
    logger.info(f"Iniciando la aplicación en el puerto {run_port}.")
    app.run(port=run_port)

    # Esperar a que ngrok termine
    if environment == "development":
        ngrok_thread.join()


if __name__ == "__main__":
    main()
