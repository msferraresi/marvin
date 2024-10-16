import sys
import time
import threading
from src import create_app
from ngrok_manager import NgrokManager  # Asegúrate de tener este archivo
import signal

environment = "development"
BOT_TOKEN = ""
ngrok_manager = None


def run_ngrok_and_set_webhook():
    global ngrok_manager
    ngrok_manager = NgrokManager(BOT_TOKEN)
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
    if len(sys.argv) > 1 and sys.argv[1] == "prod":
        environment = "production"

    # Solo ejecutar ngrok si estamos en el entorno de desarrollo
    if environment == "development":
        ngrok_thread = threading.Thread(target=run_ngrok_and_set_webhook)
        ngrok_thread.start()

    # Crear la app Flask
    app = create_app(environment)

    # Registrar el manejador de señal para cerrar ngrok al apagar la app
    signal.signal(signal.SIGINT, signal_handler)

    # Ejecutar la app Flask en el puerto 5002
    app.run(port=5002)

    # Esperar a que ngrok termine
    if environment == "development":
        ngrok_thread.join()


if __name__ == "__main__":
    main()
