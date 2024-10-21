from flask import Flask # framework pra criação de app web
from flask_sqlalchemy import SQLAlchemy # manipulação de SQL direto do python
from flask_login import LoginManager # handler de login do flask
from flask_bcrypt import Bcrypt # encriptador do flask, usa bcrypt, que é irreversível, mas reproduzível.

app = Flask(__name__)# variavel de controle do app
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:123@192.168.1.101:3306/userbase" # precisa ser o host do site
# ou, como nesse caso, o ip local. xxxx:yyyy@0.0.0.0:port x e y sao respectivamente usuario e senha da database para read/edit
app.config["SECRET_KEY"] = "5dc6d43b2e7bd8c8821d80b00ac5fde4" # algum hash aleatorio que eu criei
app.config["UPLOAD_FOLDER"] = "static/posters" # ???

database = SQLAlchemy(app) # conexao sql com o app

bcrypt = Bcrypt(app) # variavel pra uso do bcrypt
login_manager = LoginManager(app) # conexao
login_manager.login_view = "home" # define a pagina do login

from sitePy import routes # importa as rotas (links) para cada pagina do site, definido para uso do login_manager na linha de cima
# (porque foi definido aqui em baixo eu nao lembro exatamente)