from sitePy import app, database, bcrypt # ver como bcrypt funciona
from flask import render_template, url_for, redirect, jsonify, request, abort, flash
from sitePy.forms import form_login, form_newaccount, Uploader
from sitePy.models import Usuarios, Foto, InteracaoUser
from flask_login import login_required, login_user, logout_user, current_user
import os, uuid, random
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta

@app.route("/", methods=["GET","POST"])
def landingpage():
    return render_template("landingpage.html")

@app.route("/form", methods=["GET", "POST"])
def form():
    login = form_login() # funcao declarada no forms, formulario
    register = form_newaccount()

    if login.validate_on_submit(): # flask wtf form metodo
        usuario = Usuarios.query.filter_by(username=login.username.data).first() # pesquisa o usuario na database
        # checa se o usuario existe no banco + criptografa e checa contra as outras senhas criptografadas
        if not usuario:
            flash("Usuário inexistente")
        elif not bcrypt.check_password_hash(usuario.passw, login.passw.data): # caso tudo certo
            flash("Senha incorreta")
        else:
            login_user(usuario) # log in
            return redirect(url_for("profile", userid=usuario.id))
            # profile é a página pós login

    return render_template("form.html", login_form=login, register_form = register)
    # caso falso ele retorna a login_page novamente

@app.route("/newaccount", methods=["GET", "POST"])
def newaccount():
    new = form_newaccount() # outro form
    if new.validate_on_submit():

        senha = bcrypt.generate_password_hash(new.passw.data) # cria um hash novo pra senha, irreversivel
        if not Usuarios.query.filter_by(username=new.username.data).first():
            dataatual = f"{datetime.now(timezone(timedelta(hours=-3))).strftime('%Y/%m/%d')}"
            usuario = Usuarios(username=new.username.data, passw=senha, joinDate=dataatual)
        else:
            flash("Usuario já existe")
            return redirect(url_for('form'))

        database.session.add(usuario)
        database.session.commit()
        # adicionado na database
        login_user(usuario)
        # estranho, precisa só do objeto do usuario, o que poderia ser um problema caso
        # a database fosse invadida, as senhas nao seriam necessarias...
        # aparentemente "usuario" é o endereço do objeto em si, o que não fica salvo na db

        return redirect(url_for("profile", userid=usuario.id))
    else: print(new.errors)

    return render_template("form.html", register_form=new)

@app.route("/profile/<userid>", methods=["GET", "POST"])
@login_required
def profile(userid):
    manda = Uploader()
    if manda.validate_on_submit():
            image_uploader("feed-image")

    return render_template("profile.html", nome=current_user, form=manda)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    manda = Uploader()
    if manda.validate_on_submit():
        image_uploader("profile-image")
    return render_template("edit_profile.html", form=manda)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('landingpage'))

@app.route("/feed")
@login_required
def feed():
    # fotos = Foto.query.order_by(Foto.crDate.desc()).all()
    return render_template("feed.html")

@app.route("/requests/foto", methods=['GET'])
def get_fotos():
    fotos_interagidas = [interacao.image_id for interacao in InteracaoUser.query.filter_by(user_id=current_user.id).all()]

    fotos = Foto.query.filter(Foto.id.notin_(fotos_interagidas)).order_by(Foto.crDate.desc()).all()

    foto_list = [{"id": img.id,
                  "img": url_for('static', filename=f'posters/{img.img}'),
                  "owner": img.ownerID,}
                 for img in fotos]
    return jsonify(foto_list)

@app.route("/feed_all")
@login_required
def feed_all():
    img_gallery = Foto.query.order_by(Foto.crDate.desc()).all()
    return render_template("feed_all.html", img_gallery=img_gallery)

@app.route("/requests/update_counter", methods=['POST'])
def update_counter():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest": # impedir que a rota seja acessada pelo link
        abort(403)

    data = request.get_json() # recebe o JSON do request e salva em uma var
    foto_id = data.get("id") # recebe o id do javascript e coloca em uma variavel para manipulação
    action = data.get("action") # recebe o parametro inserido no JS para definir qual ação tomar
    # essencialmente essas duas variáveis "extraem" os valores que estão na var data

    foto = Foto.query.get(foto_id) # variavel pointer para o objeto com esse id
    if not foto: # caso erro
        return jsonify({"error": "foto não encontrada"}), 404

    if not InteracaoUser.query.filter_by(
        user_id = current_user.id,
        image_id = foto.id
    ).first():
        if action == "like":
            foto.likeCounter += 1
            interacao = InteracaoUser(id=random.randint(1, 1000000000), user_id=current_user.id, image_id=foto.id)
            database.session.add(interacao)
        elif action == "dislike":
            foto.dislikeCounter += 1
            interacao = InteracaoUser(id=random.randint(1, 1000000000), user_id=current_user.id, image_id=foto.id)
            database.session.add(interacao)

    database.session.commit() # salva as diferenças na DB
    return jsonify({"success": True, "likeCount": foto.likeCounter, "dislikeCount": foto.dislikeCounter}), 200
    # resposta ao script para que ele não quebre no meio e entre em combustão.

def get_unique_filename(original_name):
    # pega a extensão do arquivo
    _, ext = os.path.splitext(original_name)
    # cria nome unico com uuid e timestamp
    unique_filename = f"{datetime.now(timezone(timedelta(hours=-3))).strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}{ext}"
    # y/d/h/m/s + 8 digit uuid
    return secure_filename(unique_filename)

def image_uploader(tipo):
    manda = Uploader()
    if tipo == "feed-image":
        try:
            # Debug prints
            print("Current directory:", os.path.abspath(os.path.dirname(__file__)))
            print("Upload folder config:", app.config["UPLOAD_FOLDER"])

            arcaivo = manda.imagem.data
            safename = secure_filename(arcaivo.filename)
            unique_filename = get_unique_filename(safename)

            # Print the full path
            pathtoimg = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     app.config["UPLOAD_FOLDER"],
                                     unique_filename)
            print("Trying to save to:", pathtoimg)

            # Create directory if it doesn't exist
            upload_dir = os.path.dirname(pathtoimg)
            os.makedirs(upload_dir, exist_ok=True)

            # Try to save and print result
            arcaivo.save(pathtoimg)
            print(f"File saved as: {unique_filename}")

            # Verify file exists
            if os.path.exists(pathtoimg):
                print("File was saved successfully at:", pathtoimg)
            else:
                print("File failed to save at:", pathtoimg)

            imagem = Foto(img=unique_filename, ownerID=current_user.id)
            database.session.add(imagem)
            database.session.commit()

            return redirect(url_for("profile", userid=userid))

        except Exception as e:
            print(f"Error durante upload: {str(e)}")
            database.session.rollback()
            flash(f"Erro ao fazer upload: {str(e)}", "error")

        return render_template("profile.html", nome=current_user, form=manda)

    elif tipo == "profile-image":
        try:
            # Debug prints
            print("Current directory:", os.path.abspath(os.path.dirname(__file__)))
            print("Upload folder config:", app.config["UPLOAD_FOLDER"])

            arcaivo = manda.imagem.data
            safename = secure_filename(arcaivo.filename)
            unique_filename = get_unique_filename(safename)

            # Print the full path
            pathtoimg = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     app.config["UPLOAD_FOLDER"],
                                     unique_filename)
            print("Trying to save to:", pathtoimg)

            # Create directory if it doesn't exist
            upload_dir = os.path.dirname(pathtoimg)
            os.makedirs(upload_dir, exist_ok=True)

            # Try to save and print result
            arcaivo.save(pathtoimg)
            print(f"File saved as: {unique_filename}")

            current_user.profile_image = unique_filename
            database.session.commit()

            # Verify file exists
            if os.path.exists(pathtoimg):
                print("File was saved successfully at:", pathtoimg)
            else:
                print("File failed to save at:", pathtoimg)

            return redirect(url_for("edit_profile"))

        except Exception as e:
            print(f"Error durante upload: {str(e)}")
            database.session.rollback()
            flash(f"Erro ao fazer upload: {str(e)}", "error")

