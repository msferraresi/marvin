from werkzeug.utils import find_modules, import_string
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


def create_app(environment=None):
    app = Flask(__name__)

    if environment == "production":
        app.config.from_object("config.configPROD.ProductionConfig")
    elif environment == "development":
        app.config.from_object("config.configDEV.DevelopmentConfig")
    else:
        raise (Exception("Invalid environment"))

    ma.init_app(app)
    db.init_app(app)

    with app.app_context():
        register_blueprint(app)
        db.create_all()

    with app.app_context():
        from src.models.intentsModel import Intents

        create_initial_data(
            Intents,
            [
                {"intent_type": "greeting", "keyword": "hola"},
                {"intent_type": "greeting", "keyword": "ola"},
                {"intent_type": "greeting", "keyword": "buenas"},
                {"intent_type": "greeting", "keyword": "buenos dias"},
                {"intent_type": "greeting", "keyword": "buenas tardes"},
                {"intent_type": "greeting", "keyword": "buenas noches"},
                {"intent_type": "greeting", "keyword": "saludos"},
                {"intent_type": "greeting", "keyword": "que tal"},
                {"intent_type": "farewell", "keyword": "adios"},
                {"intent_type": "farewell", "keyword": "hasta luego"},
                {"intent_type": "farewell", "keyword": "chau"},
                {"intent_type": "farewell", "keyword": "nos vemos"},
                {"intent_type": "farewell", "keyword": "asta luego"},
                {"intent_type": "help", "keyword": "ayuda"},
                {"intent_type": "help", "keyword": "info"},
                {"intent_type": "help", "keyword": "informacion"},
                {"intent_type": "help", "keyword": "que puedo hacer"},
                {"intent_type": "help", "keyword": "que puedo pedir"},
                {"intent_type": "help", "keyword": "que puedo solicitar"},
                {"intent_type": "help", "keyword": "socorro"},
                {"intent_type": "help", "keyword": "ayudame"},
                {"intent_type": "help", "keyword": "no entiendo nada"},
            ],
        )
    return app


def register_blueprint(app):
    for module in find_modules("src.services"):
        app.register_blueprint(import_string(module).app)


def create_initial_data(model, values):
    for value in values:
        existing_data = model.query.filter_by(**value).first()
        if existing_data:
            continue
        instance = model(**value)
        db.session.add(instance)
    db.session.commit()
