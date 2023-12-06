from sitePy import app, database
from sitePy.models import Usuarios, foto
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

try:
    with app.app_context():
        database.create_all()
        print("great sucess")

    with app.app_context():
        user_instance = Usuarios(username='robson', passw='password123')
        database.session.add(user_instance)
        database.session.commit()
except SQLAlchemyError as e:
    print("erro : ", e)