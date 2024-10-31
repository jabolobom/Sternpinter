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

function showall_message(){
    imageContainer.innerHTML = "";

    const button = document.createElement("button");
    button.textContent = "Go to next page";
    button.onclick = function(){
        window.location.href = "/feed-all";
    }

    imageContainer.appendChild(button);
    console.log("botão criado") // DEBUG
}

class Swiper {
    constructor(element) {
        this.container = element

        this.handle()
    }

    handle(){
        this.images = this.container.querySelectorAll("#imageOutput")

        this.topImagem = this.images[this.images.length-1]

        if(this.images.length > 0){

            this.hammer = new Hammer(this.topImagem)
            this.hammer.add(new Hammer.Pan({
                position: Hammer.position_ALL, threshold: 0
            }))

            this.hammer.on("pan", this.onPan.bind(this))
        }
    }

onPan(e) {

  if (!this.isPanning) {

    this.isPanning = true

    // remove transição css, evita erros
    this.topImagem.style.transition = null

    // coordenadas iniciais da imagem
    let style = window.getComputedStyle(this.topImagem)
      // recebe os atributos como altura, largura
    let mx = style.transform.match(/^matrix\((.+)\)$/)
      // magia matematica maligna
    this.startPosX = mx ? parseFloat(mx[1].split(', ')[4]) : 0
    this.startPosY = mx ? parseFloat(mx[1].split(', ')[5]) : 0
    // mais magia negra

    let limites = this.topImagem.getBoundingClientRect()
      // tamanho e o posição da imagem em relação ao Viewport

      // posição do ponteiro, topo 1 ou fundo -1 da imagem
    this.isDraggingFrom =
        (e.center.y - limites.top) > this.topImagem.clientHeight / 2 ? -1 : 1
  }

  // novas coordenadas
  let posX = e.deltaX + this.startPosX
  let posY = e.deltaY + this.startPosY

  // relação entre pixels arrastados e o eixo X (matematica hell yeah)
  let propX = e.deltaX / this.container.clientWidth

  // direção arrastada esquerda -1 direita 1
  let dirX = e.deltaX < 0 ? -1 : 1 // JAVASCRIPT SYNTAX GOES BRRRRRRRRRRR

  // rotação em graus
  let deg = this.isDraggingFrom * dirX * Math.abs(propX) * 45

  // movimentando e rotando imagem
  this.topImagem.style.transform =
    'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)'

    console.log('e.deltaX:', e.deltaX, 'e.deltaY:', e.deltaY);
    console.log('posX:', posX, 'posY:', posY, 'deg:', deg);

  if (e.isFinal) {

    this.isPanning = false

    // transição volta ao normal
    this.topImagem.style.transition = 'transform 200ms ease-out'

    // reseta posição da dita cuja
    this.topImagem.style.transform = 'translateX(-50%) translateY(-50%)'

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




