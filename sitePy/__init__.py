from flask import Flask # framework pra criação de app web
from flask_sqlalchemy import SQLAlchemy # manipulação de SQL direto do python
from flask_login import LoginManager # handler de login do flask
from flask_bcrypt import Bcrypt # encriptador do flask, usa bcrypt, que é irreversível, mas reproduzível.
from flask_wtf import CSRFProtect

app = Flask(__name__)# variavel de controle do app
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:123@172.17.0.2:3306/userbase" # precisa ser o host do site
# ou, como nesse caso, o ip local. xxxx:yyyy@0.0.0.0:port x e y sao respectivamente usuario e senha da database para read/edit
# essa conexão precisa ser em um local onde tenha um MYSQL server aberto, e antes disso, é necessário rodar o
# "banco.py" para gerar as colunas necessárias na database
# no sistema teste estou usando um docker com MYSQL hosteado dentro dele, para testar no windows
# é necessário um server MYSQL rodando com a porta 3306 aberta + uma database nomeada na string acima já criada de
# antemão, pois o script banco só gera as tables (userbase = nome da database)

app.config["SECRET_KEY"] = "5dc6d43b2e7bd8c8821d80b00ac5fde4" # hash aleatório
app.config["UPLOAD_FOLDER"] = "static/posters" # pasta para salvar arquivos upados

database = SQLAlchemy(app) # conexao sql com o app

bcrypt = Bcrypt(app) # variavel pra uso do bcrypt
login_manager = LoginManager(app) # conexao
login_manager.login_view = "form" # define a pagina do login

csrf = CSRFProtect() # gerador de csrf
csrf.init_app(app)

from sitePy import routes # importa as rotas (links) para cada pagina do site, definido para uso do login_manager na linha de cima
# (porque foi definido aqui em baixo eu nao lembro exatamente)