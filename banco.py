from sitePy import app, database
from sitePy.models import Usuarios, Foto
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

try:
    with app.app_context():
        database.create_all()
        print("great sucess")
except SQLAlchemyError as e:
    print("erro : ", e)