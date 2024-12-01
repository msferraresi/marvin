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
        from src.models.intent_typesModel import IntentTypes

        create_initial_data(
            IntentTypes,
            [
                {"description": "greeting"},
                {"description": "farewell"},
                {"description": "help"},
                {"description": "information"},
            ],
        )
        create_initial_data(
            Intents,
            [
                {"intent_type_id": 1, "keyword": "hola"},
                {"intent_type_id": 1, "keyword": "ola"},
                {"intent_type_id": 1, "keyword": "buenas"},
                {"intent_type_id": 1, "keyword": "buenos dias"},
                {"intent_type_id": 1, "keyword": "buenas tardes"},
                {"intent_type_id": 1, "keyword": "buenas noches"},
                {"intent_type_id": 1, "keyword": "saludos"},
                {"intent_type_id": 1, "keyword": "que tal"},
                {"intent_type_id": 2, "keyword": "adios"},
                {"intent_type_id": 2, "keyword": "hasta luego"},
                {"intent_type_id": 2, "keyword": "chau"},
                {"intent_type_id": 2, "keyword": "nos vemos"},
                {"intent_type_id": 2, "keyword": "asta luego"},
                {"intent_type_id": 3, "keyword": "ayuda"},
                {"intent_type_id": 3, "keyword": "info"},
                {"intent_type_id": 3, "keyword": "informacion"},
                {"intent_type_id": 3, "keyword": "que puedo hacer"},
                {"intent_type_id": 3, "keyword": "que puedo pedir"},
                {"intent_type_id": 3, "keyword": "que puedo solicitar"},
                {"intent_type_id": 3, "keyword": "socorro"},
                {"intent_type_id": 3, "keyword": "ayudame"},
                {"intent_type_id": 3, "keyword": "no entiendo nada"},
                {"intent_type_id": 4, "keyword": "como te llamas?"},
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
