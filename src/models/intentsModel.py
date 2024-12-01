from src import db, ma
from src.models.intent_typesModel import IntentTypesSchema


class Intents(db.Model):
    __tablename__ = "intents"
    id = db.Column(db.Integer, primary_key=True)
    intent_type_id = db.Column(
        db.Integer, db.ForeignKey("intent_types.id"), nullable=False
    )
    keyword = db.Column(db.String(100), nullable=False, unique=True)

    intent_type = db.relationship("IntentTypes", backref="intents", lazy=True)


class IntentsSchema(ma.Schema):
    class Meta:
        model = Intents
        load_instance = True
        sqla_session = db.session
        fields = ("id", "intent_type_id", "keyword", "intent_type")

    intent_type = ma.Nested(IntentTypesSchema)
