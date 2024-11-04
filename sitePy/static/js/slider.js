let fotos = [];
let indexAtual = 0;
const CSRFTOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
const imageOutput = document.getElementById("second-imageOutput")
const firstOutput = document.getElementById("first-imageOutput")
const imageContainer = document.getElementById("imageContainer-box");

async function recebeFoto(){
    try{
        const respostaServer = await fetch("/requests/foto");
        fotos = await respostaServer.json();
        console.log(fotos)
        proxImagem();
    }
    catch (error){
        console.error("Erro no retorno de imagens: ", error) // DEBUG
    }
}
// ATTENTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
function proxImagem(){
    if (indexAtual < fotos.length) {
        if (indexAtual === 0){
            imageOutput.src = fotos[indexAtual].img;
            console.log(`current index:", ${indexAtual}, "current image:", ${imageOutput.src}, "IMAGE ID: " ${fotos[indexAtual].id}`);

            indexAtual += 1;
            firstOutput.src = fotos[indexAtual].img
            console.log(`current index:", ${indexAtual}, "current image:", ${firstOutput.src}, "IMAGE ID: " ${fotos[indexAtual].id}`)
        }
    }
    else{
        showall_message()
    }
}

class Swiper {
    constructor(element) {
        this.container = element;
        this.handle();
    }

    handle() {
        this.images = this.container.querySelectorAll(".imageOutput");

        this.topImagem = this.images[this.images.length - 1];
        this.topImagem.addEventListener('dragstart', (e) => e.preventDefault());

        if (this.images.length > 0) {
            this.hammer = new Hammer(this.topImagem, {
                inputClass: Hammer.MouseInput, // deve adicionar suporte a mouse
                recognizer: [
                    [Hammer.Pan, {
                    direction: Hammer.DIRECTION_ALL,
                    threshold: 0
                    }]
                ]
            });

            this.hammer.on("pan", this.onPan.bind(this));
        }
    }

    onPan(e) {
        let sucessful = false;

        if (!this.isPanning) {
            this.isPanning = true;

            // remove CSS transition to avoid errors
            this.topImagem.style.transition = null;

            // initial image coordinates
            let style = window.getComputedStyle(this.topImagem);
            let mx = style.transform.match(/^matrix\((.+)\)$/);
            this.startPosX = mx ? parseFloat(mx[1].split(', ')[4]) : 0;
            this.startPosY = mx ? parseFloat(mx[1].split(', ')[5]) : 0;

            let limites = this.topImagem.getBoundingClientRect();
            this.isDraggingFrom = (e.center.y - limites.top) > this.topImagem.clientHeight / 2 ? -1 : 1;
        }

        let posX = e.deltaX + this.startPosX;
        let posY = e.deltaY + this.startPosY;

        let propX = e.deltaX / this.container.clientWidth;
        let propY = e.deltaY / this.container.clientHeight;

        let dirX = e.deltaX < 0 ? -1 : 1;

        let deg = this.isDraggingFrom * dirX * Math.abs(propX) * 45;

        this.topImagem.style.transform =
            'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)';

        if (e.isFinal) {
            this.isPanning = false;

            this.topImagem.style.transition = 'transform 200ms ease-out'

            if (propX > 0.25 && e.direction === Hammer.DIRECTION_RIGHT) {

                sucessful = true;
                posX = this.container.clientWidth;

            } else if (propX < -0.25 && e.direction === Hammer.DIRECTION_LEFT) {

                sucessful = true;
                posX = -(this.container.clientWidth + this.topImagem.clientWidth);

            } else if (propY < -0.25 && e.direction === Hammer.DIRECTION_UP) {

                sucessful = true;
                posY = -(this.container.clientHeight + this.topImagem.clientHeight);

            }

            if(sucessful){
                this.topImagem.transform =
                    'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)';

                setTimeout(() => {
                    // remove a img topo
                    this.container.removeChild(this.topImagem);
                    // adiciona a próxima
                    this.push();
                    // chama o handler de movimentos
                    this.handle();
                }, 200)
            }
            else{
                this.topImagem.style.transform =
                    'translateX(-50%) translateY(-50%) rotate(0deg)';
            }

        }
    }

    push() {

        if (indexAtual < fotos.length) {
            indexAtual += 1; // PROXIMO INDEX DE IMAGEM
            // CRIA NOVO ELEMENTO IMG E COLOCA O NOME DA CLASSE
            let card = document.createElement('img');
            card.className = "imageOutput";
            // DÁ A SOURCE DA IMAGEM
            try {
                card.src = fotos[indexAtual].img
            } catch (error){
                alert("no more images", error)
            }; // TRY TO DEAL WITH UNDEFINED END OF ARRAY


            // INSERE ANTES DA QUE ESTIVER NA FRENTE
            this.container.insertBefore(card, this.container.firstChild);
            console.log("push, new image:", fotos[indexAtual], "index atual: ", indexAtual)

        } else {
            showall_message();
        }
    }
}


let swipeobj = new Swiper(imageContainer)


document.addEventListener('DOMContentLoaded', () => {
    recebeFoto(); // espera o load do resto da página antes de chamar o script
});
console.log(fotos); // DEBUG

function update_counter(action){
    const currentFoto = fotos[indexAtual]; // var para controle de qual foto está sendo manipulada
    if(!currentFoto) return; // impedir qualquer erro bizarro

    // novo request pra update
    fetch(`/requests/update_counter`,
        {
        method: "POST",
        headers:
            {
                "Content-Type": "application/json", // ? web shenanigans
                "X-Requested-With": "XMLHttpRequest", // checagem
                "X-CSRFToken": CSRFTOKEN // necessário pra que a api permita o POST
            },
            body: JSON.stringify({id: currentFoto.id, action: action}) // API espera um request em JSON
    })                                      // ID E AÇÃO, ver API para explicação
        .then(response=>{
        if(response.ok) {
            console.log(`${action} atualizado para Foto ID: ${currentFoto.id}`);
        } else {
            console.log("erro ao atualizar");
        } // handling a resposta da API
    });
}

function showall_message(){
    console.log("showmsg called")
}



