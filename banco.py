from sitePy import app, database
from sitePy.models import Usuarios, Foto
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

try: # script simples para criar as tabelas definidas em models.py
    with app.app_context():
        database.create_all()
        print("great sucess")
except SQLAlchemyError as e:
    print("erro : ", e)