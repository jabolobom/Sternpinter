from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from sitePy.models import Usuarios

#formularios são controlados por classes
class form_login(FlaskForm):
    username = StringField("username", validators=[DataRequired()]) # hard coding os formularios no back-end
    passw = PasswordField("password", validators=[DataRequired()])
    confirmButton = SubmitField("login") # submit field também é colocado no back-end

class form_newaccount(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    passw = PasswordField("password", validators=[DataRequired()])
    confirmation_passw = PasswordField("password confirmation", validators=[DataRequired(), EqualTo("passw")])
    # checa se é igual a senha
    confirmButton = SubmitField("register")

    # função simples pra checar se o usuário já existe, query de sql
    def validate_username(self, username):
        tester = Usuarios.query.filter_by(username=username.data).first() # Testa se o usuario existe na database
        if tester:
            return ValidationError("Existing user")


class Uploader(FlaskForm):
    imagem = FileField(label="nova imagem", validators=[DataRequired()])
    confirmButton = SubmitField("upload")