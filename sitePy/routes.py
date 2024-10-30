from sitePy import app, database, bcrypt # ver como bcrypt funciona
from flask import render_template, url_for, redirect, jsonify, request, abort
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

@app.route("/login_page", methods=["GET", "POST"])
def login_page():
    login = form_login() # funcao declarada no forms, formulario
    if login.validate_on_submit(): # flask wtf form metodo
        usuario = Usuarios.query.filter_by(username=login.username.data).first() # pesquisa o usuario na database
        # checa se o usuario existe no banco + criptografa e checa contra as outras senhas criptografadas
        if usuario and bcrypt.check_password_hash(usuario.passw, login.passw.data): # caso tudo certo
            login_user(usuario) # log in
            return redirect(url_for("user_page", userid=usuario.id))
            # user_page é a página pós login


    return render_template("login_page.html", form=login)
    # caso falso ele retorna a login_page novamente

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

        return redirect(url_for("user_page", userid=usuario.id))
    else: print(new.errors)

    return render_template("newaccount.html", form=new)

@app.route("/user_page/<userid>", methods=["GET", "POST"])
@login_required
def user_page(userid): # pagina do usuario
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
            return redirect(url_for("user_page", userid=userid)) # redireciona novamente a pagina do user

        return render_template("user_page.html", nome=current_user, form=manda)
    else:
        nome = Usuarios.query.get(int(userid))
    return render_template("user_page.html", nome=nome, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/feed")
@login_required
def feed():
    # fotos = Foto.query.order_by(Foto.crDate.desc()).all()
    return render_template("feed.html")

@app.route("/requests/foto", methods=['GET'])
def get_fotos():
    fotos = Foto.query.order_by(Foto.crDate.desc()).all()
    foto_list = [{"id": img.id,
                  "img": url_for('static', filename=f'posters/{img.img}'),
                  "owner": img.ownerID,}
                 for img in fotos]
    return jsonify(foto_list)

@app.route("/feed-all")
@login_required
def feed_all():
    fotos = Foto.query.order_by(Foto.crDate.desc()).all()
    return render_template("feed_all.html", fotos=fotos)

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

    if action == "like":
        foto.likeCounter += 1
    elif action == "dislike":
        foto.dislikeCounter += 1
    # define qual usar, poderia ser um MATCH case, mas não é necessário

    database.session.commit() # salva as diferenças na DB
    return jsonify({"success": True, "likeCount": foto.likeCounter, "dislikeCount": foto.dislikeCounter}), 200
    # resposta ao script para que ele não quebre no meio e entre em combustão.