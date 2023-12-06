from sitePy import app, database, bcrypt
from flask import render_template, url_for, redirect
from sitePy.forms import form_login, form_newaccount, Uploader
from sitePy.models import Usuarios, Foto
from flask_login import login_required, login_user, logout_user, current_user
import os
from werkzeug.utils import secure_filename

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/pagetwo", methods=["GET", "POST"])
def pagetwo():
    login = form_login()
    if login.validate_on_submit():
        usuario = Usuarios.query.filter_by(username=login.username.data).first()
        if usuario and bcrypt.check_password_hash(usuario.passw, login.passw.data):
            login_user(usuario)
            return redirect(url_for("after", userid=usuario.id))


    return render_template("pagetwo.html", form=login)

@app.route("/newaccount", methods=["GET", "POST"])
def newaccount():
    new = form_newaccount()
    if new.validate_on_submit():

        senha = bcrypt.generate_password_hash(new.passw.data)
        usuario = Usuarios(username=new.username.data, passw=senha)

        database.session.add(usuario)
        database.session.commit()
        login_user(usuario)

        return redirect(url_for("after", userid=usuario.id))
    else: print(new.errors)

    return render_template("newaccount.html", form=new)

@app.route("/after/<userid>", methods=["GET", "POST"])
@login_required
def after(userid):
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


