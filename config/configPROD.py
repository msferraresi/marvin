class Config:
    """Configuración general"""

    DEBUG = False  # Desactivado en producción
    TESTING = False
    TELEGRAM_TOKEN = "tu-token-de-telegram-produccion"
    TELEGRAM_API = "https://api.telegram.org/bot[TOKEN]/"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CHATGPT_API_KEY = ""
    GEMINI_API_KEY = ""
    MINIMUN_LOGGER_DETAIL = "INFO"


class ProductionConfig(Config):
    """Configuración para el entorno de producción"""

    ENV = "production"
    SECRET_KEY = "produccion-secreto"
    NAME_DB = "marvin"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{NAME_DB}_{ENV}.db"
    RUN_PORT = 5002
