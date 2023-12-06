from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from sitePy.models import Usuarios

class form_login(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    passw = PasswordField("password", validators=[DataRequired()])
    confirmButton = SubmitField("login")

class form_newaccount(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    passw = PasswordField("password", validators=[DataRequired()])
    confirmation_passw = PasswordField("password confirmation", validators=[DataRequired(), EqualTo("passw")])
    confirmButton = SubmitField("register")

    def validate_username(self, username):
        tester = Usuarios.query.filter_by(username=username.data).first() # Testa se o usuario existe na database
        if tester:
            return ValidationError("Existing user")


class Uploader(FlaskForm):
    imagem = FileField(label="nova imagem", validators=[DataRequired()])
    confirmButton = SubmitField("upload")