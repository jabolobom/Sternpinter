from sitePy import app, database, bcrypt
from flask import render_template, url_for, redirect, jsonify, request, abort, flash # flash serve para mostrar mensage-
# ns de erro dentro do html, sem alertas
from sitePy.forms import form_login, form_newaccount, Uploader
from sitePy.models import Usuarios, Foto, InteracaoUser
from flask_login import login_required, login_user, logout_user, current_user
import os, uuid, random
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
# libraries úteis para algumas funções
@app.route("/", methods=["GET","POST"]) # "/" é sempre a homepage de uma api Flask
def landingpage():
    return render_template("landingpage.html")

@app.route("/form", methods=["GET", "POST"]) # página de login
def form():
    login = form_login() # funcao declarada no forms, formulario de login
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
            # redireciona ao perfil do usuário

    return render_template("form.html", login_form=login, register_form = register)
    # caso aconteça algum erro no formulário ele retorna a login_page novamente

@app.route("/newaccount", methods=["GET", "POST"]) # formulário de criação de conta
def newaccount(): # esse formulário existe simultaneamente ao formulário de login (mesma página)
    new = form_newaccount() # o formulário chamado é diferente dependendo de qual função é requisitada
    if new.validate_on_submit():

        senha = bcrypt.generate_password_hash(new.passw.data) # cria um hash novo pra senha, irreversivel
        if not Usuarios.query.filter_by(username=new.username.data).first(): # busca se o usuário já existe
            dataatual = f"{datetime.now(timezone(timedelta(hours=-3))).strftime('%Y/%m/%d')}"
            usuario = Usuarios(username=new.username.data, passw=senha, joinDate=dataatual)
            # não existindo, cria um novo
        else:
            flash("Usuario já existe")
            return redirect(url_for('form'))

        database.session.add(usuario)
        database.session.commit()
        # adicionado na database
        login_user(usuario)
        # talvez fosse interessante colocar o usuário em um hash também, para aumentar a segurança

        return redirect(url_for("profile", userid=usuario.id))
    else: print(new.errors) # caso algo aconteça

    return render_template("form.html", register_form=new)
    # se o formulário não for validado, o fallback é atualizar a página
@app.route("/profile/<userid>", methods=["GET", "POST"]) # perfil do usuário
@login_required # checa se o usuário está logado, method do flask
def profile(userid):
    manda = Uploader() # instancia o gerenciador de upload
    if manda.validate_on_submit(): # metodo padrão, já que uploader herda de flaskform
            image_uploader("feed-image") # função de upload, explicação na própria...

    return render_template("profile.html", nome=current_user, form=manda)
    # depois do fim do upload, refresh
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required # edição do perfil, permite mudar a imagem de perfil e excluir a conta
def edit_profile():
    manda = Uploader()
    if manda.validate_on_submit(): # mesma ideia que o perfil
        image_uploader("profile-image") # chama a função com um argumento diferente
    return render_template("edit_profile.html", form=manda)

@app.route("/logout") # logout simples
@login_required
def logout():
    logout_user() # controle interno, função builtin flask
    return redirect(url_for('landingpage')) # homepage

@app.route("/feed")
@login_required
def feed():
    return render_template("feed.html") # lógica de disposição de imagens e carrossel controlada pelo
    # CSS e Javascript

@app.route("/requests/foto", methods=['GET']) # função usada no swiper para enviar imagens para o script
def get_fotos():
    fotos_interagidas = [interacao.image_id for interacao in InteracaoUser.query.filter_by(user_id=current_user.id).all()]
    # checa imagens que já foram interagidas pelo current_user (current_user builtin flask)
    fotos = Foto.query.filter(Foto.id.notin_(fotos_interagidas)).order_by(Foto.crDate.desc()).all()
    # cria uma lista com as fotos não interagidas
    foto_list = [{"id": img.id,
                  "img": url_for('static', filename=f'posters/{img.img}'),
                  "owner": img.ownerID,}
                 for img in fotos]
    # envia como JSON para o script da página
    return jsonify(foto_list)

@app.route("/feed_all") # envia todas fotos da database para o HTML/CSS da página
@login_required
def feed_all():
    img_gallery = Foto.query.order_by(Foto.crDate.desc()).all()
    return render_template("feed_all.html", img_gallery=img_gallery)
    # envia uma variável img_gallery para ser usada na sintaxe de Jinja2 (python scripts no html)
@app.route("/requests/update_counter", methods=['POST']) # rota para modificar os likes/dislikes
def update_counter():
    if request.headers.get("X-Requested-With") != "XMLHttpRequest": # impedir que a rota seja acessada pelo link
        abort(403)

    data = request.get_json() # recebe o JSON do request e salva em uma var
    foto_id = data.get("id") # recebe o id da imagem e coloca em uma variavel para manipulação
    action = data.get("action") # recebe o parametro inserido no JS para definir qual ação tomar
    # essencialmente essas duas variáveis "extraem" os valores que estão na var data

    foto = Foto.query.get(foto_id) # variavel pointer para o objeto com esse id
    if not foto: # caso erro
        return jsonify({"error": "foto não encontrada"}), 404

    if not InteracaoUser.query.filter_by(
        user_id = current_user.id,
        image_id = foto.id
    ).first(): # se não há interação
        if action == "like": # cria uma nova interação, aumentando o contador de likes
            # e criando uma nova instância na classe interacao. Vice-versa para dislike
            foto.likeCounter += 1
            interacao = InteracaoUser(id=random.randint(1, 1000000000), user_id=current_user.id, image_id=foto.id)
            # id random para satisfazer os requisitos da DB de ter uma key_primária
            database.session.add(interacao)
        elif action == "dislike":
            foto.dislikeCounter += 1
            interacao = InteracaoUser(id=random.randint(1, 1000000000), user_id=current_user.id, image_id=foto.id)
            database.session.add(interacao)

    database.session.commit() # salva as diferenças na DB
    return jsonify({"success": True, "likeCount": foto.likeCounter, "dislikeCount": foto.dislikeCounter}), 200
    # resposta ao script para que ele não quebre no meio e entre em combustão.

@app.route("/delete_account_call", methods=['POST'])
def delete_account():
    # copiado do meu commit no git:
    # + função de delete na rota, apaga o usuário e todos relacionamentos
    # (imagens upadas + interações na db
    # [entretanto os valores adicionados pelas interações continuam nas imagens que foram interagidas,
    # não faria sentido remover essas também])
    try:

        for foto in current_user.fotos:
            if os.path.exists(foto.img):
                os.remove(foto.img)
            database.session.delete(foto)
            # deleta todas fotos upadas pelo usuário

        if current_user.profile_image != "default-profile.jpg":
            profile_image_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                app.config["UPLOAD_FOLDER"],
                current_user.profile_image
            ) # deleta a foto de perfil do usuário, um pouco mais complexo, considerando que a classe
            # usuário salva apenas o nome da imagem, e a imagem em si não fica registrada na DB de fotos
            # apesar de fisicamente estar no mesmo diretório.
            if os.path.exists(profile_image_path):
                os.remove(profile_image_path)  # exclui a imagem
            current_user.profile_image = "default-profile.jpg" # volta a padrão pra nao dar erro na db/classe

        database.session.query(InteracaoUser).filter_by(user_id=current_user.id).delete()
        Usuarios.query.filter_by(id=current_user.id).delete()
        database.session.commit()

        return jsonify({"Mensagem": "Conta deletada"}), 200
    except Exception as e:
        return jsonify({"ERRO": str(e)}), 500

def get_unique_filename(original_name): # criar nome único para as imagens, para evitar imagens repetidas
    # quando requisitadas
    _, ext = os.path.splitext(original_name) # pega a extensão do arquivo
    # cria nome unico com uuid e timestamp
    unique_filename = f"{datetime.now(timezone(timedelta(hours=-3))).strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}{ext}"
    # y/d/h/m/s + 8 digitos de uuid
    return secure_filename(unique_filename) # retorna o nome

def image_uploader(tipo): # gerenciador de uploads, argumento define que tipo de imagem está sendo enviada
    manda = Uploader()
    if tipo == "feed-image": # imagem de feed, aparece no swiper e na galeria principal
        try:
            arcaivo = manda.imagem.data
            safename = secure_filename(arcaivo.filename)
            unique_filename = get_unique_filename(safename) # recebe o nome seguro

            pathtoimg = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     app.config["UPLOAD_FOLDER"],
                                     unique_filename)

            # cria a pasta se ela não existir (provavelmente não vá acontecer)
            upload_dir = os.path.dirname(pathtoimg)
            os.makedirs(upload_dir, exist_ok=True)
            # salva a imagem
            arcaivo.save(pathtoimg)

            imagem = Foto(img=unique_filename, ownerID=current_user.id) # instancia nova imagem na DB
            database.session.add(imagem) # adiciona
            database.session.commit() # salva

            return redirect(url_for("profile", userid=userid))

        except Exception as e:
            database.session.rollback()
            flash(f"Erro ao fazer upload: {str(e)}", "error")
            # provavelmente não vá acontecer, mas fallback de erro

        return render_template("profile.html", nome=current_user, form=manda)

    elif tipo == "profile-image": # imagem de perfil, não fica salva na DB como as outras
        # fica salva na classe usuário
        try:
            arcaivo = manda.imagem.data
            safename = secure_filename(arcaivo.filename)
            unique_filename = get_unique_filename(safename)

            pathtoimg = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     app.config["UPLOAD_FOLDER"],
                                     unique_filename)

            upload_dir = os.path.dirname(pathtoimg)
            os.makedirs(upload_dir, exist_ok=True)

            arcaivo.save(pathtoimg)
            # função essencialmente igual, só muda essa linha e o retorno
            current_user.profile_image = unique_filename
            # muda o profile image do current user para a imagem que foi enviada
            database.session.commit()

            return redirect(url_for("edit_profile")) # atualiza a página

        except Exception as e:
            database.session.rollback()
            flash(f"Erro ao fazer upload: {str(e)}", "error")
            # fallback de erro
