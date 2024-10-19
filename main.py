import sys
import time
import threading
from src import create_app
from ngrok_manager import NgrokManager  # Asegúrate de tener este archivo
import signal

ngrok_manager = None


def run_ngrok_and_set_webhook(bot_token):
    global ngrok_manager
    ngrok_manager = NgrokManager(bot_token)
    ngrok_manager.run_ngrok()
    time.sleep(5)

    if public_url := ngrok_manager.get_public_url():
        ngrok_manager.set_telegram_webhook(public_url)
    else:
        print("No se pudo obtener la URL pública de ngrok.")


def signal_handler(sig, frame):
    global ngrok_manager
    print("Cerrando la aplicación...")
    if ngrok_manager:
        ngrok_manager.stop_ngrok()
    sys.exit(0)


def main():
    global environment

    environment = "development" if len(sys.argv) == 1 else sys.argv[1]

    app = create_app(environment)

    bot_token = app.config.get("TELEGRAM_TOKEN")

    if not bot_token:
        print("Error: BOT_TOKEN no encontrado en la configuración.")
        sys.exit(1)

    if environment == "development":
        ngrok_thread = threading.Thread(
            target=run_ngrok_and_set_webhook, args=(bot_token,)
        )
        ngrok_thread.start()

    signal.signal(signal.SIGINT, signal_handler)

    # Ejecutar la app Flask en el puerto 5002
    app.run(port=5002)

    # Esperar a que ngrok termine
    if environment == "development":
        ngrok_thread.join()


if __name__ == "__main__":
    main()
