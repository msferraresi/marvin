class Config:
    """Configuración general"""

    DEBUG = True  # Activa el modo de depuración para desarrollo
    TESTING = False
    TELEGRAM_TOKEN = "tu-token-de-telegram"
    TELEGRAM_API = "https://api.telegram.org/bot[TOKEN]/"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CHATGPT_API_KEY = ""
    GEMINI_API_KEY = ""
    MINIMUN_LOGGER_DETAIL = "INFO"



class DevelopmentConfig(Config):
    """Configuración para el entorno de desarrollo"""

    ENV = "development"
    SECRET_KEY = "desarrollo-secreto"
    NAME_DB = "marvin"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{NAME_DB}_{ENV}.db"
    RUN_PORT = 5002
