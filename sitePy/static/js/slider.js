import Hammer from 'hammerjs';


let fotos = [];
let indexAtual = 0;
const CSRFTOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
const imageOutput = document.getElementById("imageOutput")
const imageContainer = document.getElementById("imageContainer-box");

async function recebeFoto(){
    try{
        const respostaServer = await fetch("/requests/foto");
        fotos = await respostaServer.json();''
        proxImagem();
    }
    catch (error){
        console.error("Erro no retorno de imagens: ", error) // DEBUG
    }
}
// ATTENTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
function proxImagem(){
    if (indexAtual < fotos.length) {
        imageOutput.src = fotos[indexAtual].img;
        console.log(`Current image: ${imageOutput.src}`); // DEBUG
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
        this.images = this.container.querySelectorAll("#imageOutput");

        this.topImagem = this.images[this.images.length - 1];

        if (this.images.length > 0) {
            this.hammer = new Hammer(this.topImagem);
            this.hammer.add(new Hammer.Pan({
                direction: Hammer.DIRECTION_ALL,
                threshold: 0
            }));
            this.hammer.add(new Hammer.Mouse());

            this.hammer.on("pan", this.onPan.bind(this));
        }
    }

    onPan(e) {
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

        console.log('e.deltaX:', e.deltaX, 'e.deltaY:', e.deltaY);
        console.log('posX:', posX, 'posY:', posY, 'deg:', deg);

        if (e.isFinal) {
            this.isPanning = false;

            this.topImagem.style.transform = 'translateX(-50%) translateY(-50%) rotate(0deg)';

            if (propX > 0.25 && e.direction === Hammer.DIRECTION_RIGHT) {
                posX = this.container.clientWidth;
                this.topImagem.style.transform =
                    'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)';
            } else if (propX < -0.25 && e.direction === Hammer.DIRECTION_LEFT) {
                posX = -(this.container.clientWidth + this.topImagem.clientWidth);
                this.topImagem.style.transform =
                    'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)';
            } else if (propY < -0.25 && e.direction === Hammer.DIRECTION_UP) {
                posY = -(this.container.clientHeight + this.topImagem.clientHeight);
                this.topImagem.style.transform =
                    'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)';
            } else {
                this.topImagem.style.transform =
                    'translateX(-50%) translateY(-50%) rotate(0deg)';
            }
        }
    }
}


let swipeobj = new Swiper(imageContainer)


recebeFoto(); // chama a função quando o script é carregado
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




