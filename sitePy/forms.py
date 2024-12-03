from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from sitePy.models import Usuarios

# FORMULÁRIOS DO SITE. NA UTILIZAÇÃO DO FLASK, SÃO CLASSES HERDADAS DE FlaskForm
class form_login(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()]) # hard coding os formularios no back-end
    passw = PasswordField("Senha", validators=[DataRequired()])
    confirmButton = SubmitField("Login", render_kw={"class": "confirm-btn"}) # submit field também é colocado no back-end

class form_newaccount(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    passw = PasswordField("Senha", validators=[DataRequired()])
    confirmation_passw = PasswordField("Confirmação de senha", validators=[DataRequired(), EqualTo("passw")])
    # checa se é igual a senha
    confirmButton = SubmitField("Criar conta", render_kw={"class": "confirm-btn"})

    # função simples pra checar se o usuário já existe, query de sql
    def validate_username(self, username):
        tester = Usuarios.query.filter_by(username=username.data).first() # Testa se o usuario existe na database
        if tester:
            return ValidationError("Existing user")


class Uploader(FlaskForm): # gerencia upload de arquivos
    imagem = FileField(label="nova imagem", validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], "Apenas arquivos de imagem: jpg,jpeg,png e gif's permitidos.")])
    confirmButton = SubmitField("Upload")