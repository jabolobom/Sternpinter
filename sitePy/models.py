from sitePy import database, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(userID):
    return Usuarios.query.get(int(userID))

class Usuarios(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(255), nullable=False, unique=True)
    passw = database.Column(database.String(255), nullable=False)
    fotos = database.relationship('Foto', backref='Usuarios', lazy=True)

class Foto(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    img = database.Column(database.String(255), default="default.png")
    crDate = database.Column(database.DateTime, nullable=False, default=datetime.utcnow())
    ownerID = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)
