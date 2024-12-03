let fotos = []; // array para guardar as imagens
let indexAtual = 0; // index do array
const CSRFTOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
const imageOutput = document.getElementById("second-imageOutput")
const firstOutput = document.getElementById("first-imageOutput")
// gambiarra maldita produzida das profundezas da minha mente febril
// essencialmente a primeira imagem da pilha e a próxima
// possivelmente (com certeza) existe um jeito melhor de fazer isso funcionar
const imageContainer = document.getElementById("imageContainer-box"); // autoexplicativo
let topImageIndex = 0; // index da imagem de cima atual, o indexa atual sempre vai estar 1 a frente disso

async function recebeFoto(){ // api call pra receber as fotos da database
    try{
        const respostaServer = await fetch("/requests/foto");
        fotos = await respostaServer.json();
        console.log(fotos)
        if (fotos.length === 0){
            aviso() // se não houver fotos que ainda não foram interagidas, exibe um alerta e redireciona
        }
        else{
            proxImagem(); // se houverem novas imagens, continua com o swiper normalmente
        }

    }
    catch (error){
        console.error("Erro no retorno de imagens: ", error) // DEBUG
    }
}

function proxImagem(){
    if (indexAtual < fotos.length) {
        if (indexAtual === 0){ // "===" POR QUE TÃO HORROROSO JAVASCRIPT
            imageOutput.src = fotos[indexAtual].img; // fotos.nome (img)
            console.log(`current index:", ${indexAtual}, "current image:", ${imageOutput.src}, "IMAGE ID: " ${fotos[indexAtual].id}`);
            // debug :)
            indexAtual += 1; // proxima
            firstOutput.src = fotos[indexAtual].img
            console.log(`current index:", ${indexAtual}, "current image:", ${firstOutput.src}, "IMAGE ID: " ${fotos[indexAtual].id}`)
        }
    }
} // na verdade essa função só é chamada na inicialização do script, depois disso quem gerencia as próximas
// imagens é um métod dentro da classe swiper

function aviso(){ // autoexplicativo, redireciona ao feed all caso o usuário tenha interagido com tudo
    console.log("empty array")
    alert("Você já interagiu com todas as imagens... Redirecionando...");
    window.location.href= feedAll_url
}

class Swiper {
    constructor(element) {
        this.container = element;
        this.handle();
    } // __init__

    handle() { // gerenciador de gestos, é aqui que o hammer.js faz a mágica dele
        this.images = this.container.querySelectorAll(".imageOutput");

        this.topImagem = this.images[this.images.length - 1];
        this.topImagem.addEventListener('dragstart', (e) => e.preventDefault());
        // impede que a imagem seja "arrastada", evita alguns bugs
        if (this.images.length > 0) { // se existe uma imagem
            this.hammer = new Hammer(this.topImagem, { // cria uma instância de hammer
                inputClass: Hammer.MouseInput, // adiciona suporte a mouse
                recognizer: [
                    [Hammer.Pan, { // reconhece movimento de pan (tipo arrastar)
                    direction: Hammer.DIRECTION_ALL, // em todas direções
                    threshold: 0 // qualquer movimento segurando o clique já arrasta, não tem threshold
                    }]
                ]
            });

            this.hammer.on("pan", this.onPan.bind(this)); // binda o hammer ao objeto novo
        }
    }

    onPan(e) { // ao mexer a imagem, essa função é executada
        let sucessful = false;

        if (!this.isPanning) {
            this.isPanning = true; // movimento começa

            // remove transições de CSS para evitar qualquer problema
            this.topImagem.style.transition = null;
            // coordenadas iniciais da imagem
            let style = window.getComputedStyle(this.topImagem);
            let mx = style.transform.match(/^matrix\((.+)\)$/);
            // matriz = MAGIA NEGRA (posicionamento)
            this.startPosX = mx ? parseFloat(mx[1].split(', ')[4]) : 0;
            this.startPosY = mx ? parseFloat(mx[1].split(', ')[5]) : 0;
            // yer a wizard harry!
            let limites = this.topImagem.getBoundingClientRect();
            // limite do arrasta
            this.isDraggingFrom = (e.center.y - limites.top) > this.topImagem.clientHeight / 2 ? -1 : 1;
            // de que direção está sendo arrastado (esquerda - direita...)
        }


        let posX = e.deltaX + this.startPosX;
        let posY = e.deltaY + this.startPosY;
        // transformação de posição
        let propX = e.deltaX / this.container.clientWidth;
        let propY = e.deltaY / this.container.clientHeight;
        // movimentação em ambos eixos
        let dirX = e.deltaX < 0 ? -1 : 1;

        let deg = this.isDraggingFrom * dirX * Math.abs(propX) * 45;
        // rotação leve ( frescurinhas )
        this.topImagem.style.transform =
            'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)';
        // animação de movimento
        if (e.isFinal) { // quando o mouse é solto, esse if se torna true e é executado
            this.isPanning = false; // movimento acaba

            this.topImagem.style.transition = 'transform 200ms ease-out' // transição retorna ao lugar
            // se passar de um certo threshold para direita ou esquerda, lida de formas diferentes
            if (propX > 0.25 && e.direction === Hammer.DIRECTION_RIGHT) {
                sucessful = true; // garante que ocorreu o movimento
                posX = this.container.clientWidth; // volta a posição inicial
                update_counter("like", topImageIndex); // chama a api pedindo um contador de like
                console.log("top image index: ", topImageIndex) // debug
            } else if (propX < -0.25 && e.direction === Hammer.DIRECTION_LEFT) {
                sucessful = true;
                posX = -(this.container.clientWidth + this.topImagem.clientWidth);
                update_counter("dislike", topImageIndex); // mesma coisa que a de cima, apenas pro dislike
                console.log("top image index: ", topImageIndex)
            }

            if(sucessful){ // se funcionou
                this.topImagem.transform = // joga a "carta" da imagem fora
                    'translateX(' + posX + 'px) translateY(' + posY + 'px) rotate(' + deg + 'deg)';

                setTimeout(() => { // esse aqui é engraçado, parece não ser necessário, já que quando
                    // o mouse é solto a função reseta, mas na verdade antes disso era possível que o usuário clicasse
                    // rapidamente e puxasse a próxima carta pra posição do mouse instantaneamente, por isso o timeout
                    // imperceptível se fez necessário
                    // remove a img topo
                    this.container.removeChild(this.topImagem); // remove a imagem jogada fora
                    // adiciona a próxima
                    this.push();
                }, 200)
            }
            else{
                this.topImagem.style.transform =
                    'translateX(-50%) translateY(-50%) rotate(0deg)'; // se não tiver sucesso reseta a carta
            } // ( lida com situações em que a carta é puxada para cima e para baixo

        }
    }

    push() { // métod que gerencia a próxima imagem da stack
        if (indexAtual < fotos.length - 1) { // checa se tem mais imagens
            topImageIndex = indexAtual;
            indexAtual += 1; // proximo index de imagem
            // cria um novo elemento img e coloca a classe certa nela
            let card = document.createElement('img');
            card.className = "imageOutput";
            // fonte da imagem
            card.src = fotos[indexAtual].img
            // chama o handler de movimentos
            this.handle();

            // insere antes da imagem do topo
            this.container.insertBefore(card, this.container.firstChild);
            console.log("push, new image:", fotos[indexAtual], "index atual: ", indexAtual);
            // terminado o processo

        } else if (indexAtual === fotos.length - 1){ // checa se é a ultima
                console.log("ultima imagem");
                this.handle();
                indexAtual += 1;
                topImageIndex = indexAtual - 1; // seguindo a estrutura anterior sem essa mudança acabaria que
                // update_count(y, x)
                // seria chamado com um index além do que existe dentro da array fotos, o que geraria um erro
        } else if (indexAtual >= fotos.length){ // sem mais imagens, fim da array
            aviso(); // alerta e redirecionamento
        }
    }
}

let swipeobj = new Swiper(imageContainer) // instancia o Swiper

document.addEventListener('DOMContentLoaded', () => {
    recebeFoto(); // espera o load do resto da página antes de chamar o script, sem isso aconteciam alguns bugs
});

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
    })                                      // ID E AÇÃO, ver rota API para explicação
        .then(response=>{
        if(response.ok) {
            console.log(`${action} atualizado para Foto ID: ${currentFoto.id}`);
        } else {
            console.log("erro ao atualizar");
        } // lidando com a resposta da API
    });
}

function update_counter(action, index){ // action pra definir dislike ou like em uma função só
    // index como parametro para evitar mudar a imagem errada na DB (pode ser que a função push seja chamada antes
    // do update_counter
    // usar a variável, é uma concorrência que pode acontecer, não acho que aconteceria frequentemente,
    // mas poderia ter uma chance, logo é melhor prevenir
    const currentFoto = fotos[index]; // var para controle de qual foto está sendo manipulada
    if(!currentFoto) return; // impedir qualquer erro bizarro de index
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
        } // lidando com a resposta da API, não precisa necessariamente printar algo, ou até fazer algo
            // mas é necessário que exista um .then que receba a mensagem de resposta
    });
}


