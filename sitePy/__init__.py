from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:123@192.168.1.101:3306/userbase" # mudar para o ip do host onde
# o container está
app.config["SECRET_KEY"] = "5dc6d43b2e7bd8c8821d80b00ac5fde4"
app.config["UPLOAD_FOLDER"] = "static/posters"

database = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "home"

from sitePy import routes