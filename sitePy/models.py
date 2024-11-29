from sitePy import database, login_manager
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin

@login_manager.user_loader
def load_user(userID):
    return Usuarios.query.get(int(userID))
# duas classes, cada uma para uma tabela, as infos sao inseridas atraves de um formulario
# kinda ingenious

class Usuarios(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True) # uso interno, associação com imagens
    username = database.Column(database.String(255), nullable=False, unique=True) # login
    passw = database.Column(database.String(255), nullable=False) # login, vai ser escrita em um hash irreversivel
    joinDate = database.Column(database.String(255), nullable=False)
    fotos = database.relationship('Foto', backref='usuarios', lazy=True, cascade="all, delete-orphan")
    interacao = database.relationship("InteracaoUser", backref='usuarios', lazy=True, cascade="all, delete-orphan")
    profile_image = database.Column(database.String(255), default="default-profile.jpg")

class Foto(database.Model):
    id = database.Column(database.Integer, primary_key = True) # uso interno
    img = database.Column(database.String(255), default="default.png")
    crDate = database.Column(database.DateTime, nullable=False, default=datetime.now(timezone(timedelta(hours=-3))))
    likeCounter = database.Column(database.Integer, default=0)
    dislikeCounter = database.Column(database.Integer, default=0)
    ownerID = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)
    # owner id recebe uma foreign key, é mais uma solução de base de dados do que uma solução orientada a objetos
    # (apesar de ser um atributo), essa foreign key é um valor de uma outra base de dados. Essencialmente é o que
    # conecta uma a outra.
    interacao = database.relationship("InteracaoUser", backref='foto', lazy=True, cascade="all, delete-orphan")

class InteracaoUser(database.Model):
    id = database.Column(database.Integer, primary_key=True) # toda classe precisa de uma primaria, apeasr de que não será usada
    user_id = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)
    image_id = database.Column(database.Integer, database.ForeignKey('foto.id'), nullable=False)
