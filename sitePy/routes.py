from sitePy import app, database, bcrypt # ver como bcrypt funciona
from flask import render_template, url_for, redirect
from sitePy.forms import form_login, form_newaccount, Uploader
from sitePy.models import Usuarios, Foto
from flask_login import login_required, login_user, logout_user, current_user
import os
from werkzeug.utils import secure_filename

# esse codigo permite que todas as rotas do site estejam definidas em um só lugar
@app.route("/")
def home():
    return render_template('home.html')
    # render template essencialmente carrega um html
    # redirect funciona igual, auto-explicativo

@app.route("/pagetwo", methods=["GET", "POST"])
def pagetwo():
    login = form_login() # funcao declarada no forms, formulario
    if login.validate_on_submit(): # flask wtf form metodo
        usuario = Usuarios.query.filter_by(username=login.username.data).first() # pesquisa o usuario na database
        # checa se o usuario existe no banco + criptografa e checa contra as outras senhas criptografadas
        if usuario and bcrypt.check_password_hash(usuario.passw, login.passw.data): # caso tudo certo
            login_user(usuario) # log in
            return redirect(url_for("after", userid=usuario.id))
            # after é a página pós login


    return render_template("pagetwo.html", form=login)
    # caso falso ele retorna a pagetwo novamente

@app.route("/newaccount", methods=["GET", "POST"])
def newaccount():
    new = form_newaccount() # outro form
    if new.validate_on_submit():


        senha = bcrypt.generate_password_hash(new.passw.data) # cria um hash novo pra senha, irreversivel
        usuario = Usuarios(username=new.username.data, passw=senha)

        database.session.add(usuario)
        database.session.commit()
        # adicionado na database
        login_user(usuario)
        # estranho, precisa só do objeto do usuario, o que poderia ser um problema caso
        # a database fosse invadida, as senhas nao seriam necessarias...
        # aparentemente "usuario" é o endereço do objeto em si, o que não fica salvo na db

        return redirect(url_for("after", userid=usuario.id))
    else: print(new.errors)

    return render_template("newaccount.html", form=new)

@app.route("/after/<userid>", methods=["GET", "POST"])
@login_required
def after(userid): # pagina do usuario
    if int(userid) == int(current_user.id):
        manda = Uploader()
        if manda.validate_on_submit():
            arcaivo = manda.imagem.data
            safename = secure_filename(arcaivo.filename)

            pathtoimg = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config["UPLOAD_FOLDER"],safename)
            arcaivo.save(pathtoimg)

            imagem = Foto(img=safename, ownerID=current_user.id)

            database.session.add(imagem)
            database.session.commit()

        return render_template("after.html", nome=current_user, form=manda)
    else:
        nome = Usuarios.query.get(int(userid))
    return render_template("after.html", nome=nome, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.crDate.desc()).all()
    return render_template("feed.html", fotos=fotos)


