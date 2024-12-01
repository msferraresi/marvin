from src import db, ma


class IntentTypes(db.Model):
    __tablename__ = "intent_types"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False, unique=True)


class IntentTypesSchema(ma.Schema):
    class Meta:
        model = IntentTypes
        load_instance = True
        sqla_session = db.session
        fields = ("id", "description")
