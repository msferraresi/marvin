from src import db, ma


class Intents(db.Model):
    __tablename__ = "intents"
    id = db.Column(db.Integer, primary_key=True)
    intent_type = db.Column(db.String(100), nullable=False)
    keyword = db.Column(db.String(100), nullable=False, unique=True)


class IntentsSchema(ma.Schema):
    class Meta:
        model = Intents
        load_instance = True
        sqla_session = db.session
        fields = ("id", "intent_type", "keyword")
