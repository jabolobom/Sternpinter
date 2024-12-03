from sitePy import database, login_manager
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin # possibilita alguns checks em relação ao login do usuário, como checar
# se está realmente logado ou não.

# ARQUIVO DE TABELAS DA DATABASE
@login_manager.user_loader
def load_user(userID): # função necessária do flask, se envolve login, precisa de um user loader
    return Usuarios.query.get(int(userID))

# duas classes, cada uma para uma tabela, as infos sao inseridas atraves de um formulario
class Usuarios(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True) # uso interno, associação com imagens
    username = database.Column(database.String(255), nullable=False, unique=True) # username login
    passw = database.Column(database.String(255), nullable=False) # login, vai ser escrita em um hash irreversivel
    joinDate = database.Column(database.String(255), nullable=False)
    fotos = database.relationship('Foto', backref='usuarios', lazy=True, cascade="all, delete-orphan")
    # relacionamento com foto; se refere as imagens enviadas pelo usuário
    interacao = database.relationship("InteracaoUser", backref='usuarios', lazy=True, cascade="all, delete-orphan")
    # relacionamento com interacaouser; se refere a que imagens o usuário já interagiu no swiper
    profile_image = database.Column(database.String(255), default="default-profile.jpg") # imagem de perfil

class Foto(database.Model):
    id = database.Column(database.Integer, primary_key = True) # uso interno
    img = database.Column(database.String(255), default="default.png") # nome do arquivo
    crDate = database.Column(database.DateTime, nullable=False, default=datetime.now(timezone(timedelta(hours=-3))))
    # para definir quais imagens aparecem primeiro no swiper (LIFO)
    likeCounter = database.Column(database.Integer, default=0)
    # quantidade de deslizadas para direita
    dislikeCounter = database.Column(database.Integer, default=0)
    # qnt para esquerda
    ownerID = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)
    # owner id recebe uma foreign key, é mais uma solução de base de dados do que uma solução orientada a objetos
    # (apesar de ser um atributo), essa foreign key é um valor de uma outra base de dados. Essencialmente é o que
    # conecta uma a outra.
    interacao = database.relationship("InteracaoUser", backref='foto', lazy=True, cascade="all, delete-orphan")
    # delete-orphan se refere aos relacionamentos de interação, quando a conta é deletada, todos relacionamentos vão
    # junto.

class InteracaoUser(database.Model):
    id = database.Column(database.Integer, primary_key=True) # toda classe precisa de uma primaria, apeasr de que não será usada
    user_id = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)
    image_id = database.Column(database.Integer, database.ForeignKey('foto.id'), nullable=False)
    # auto-explicativo; salva todas interações do Y user id com X imagem id