let fotos = [];
let indexAtual = 0;
const CSRFTOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

async function recebeFoto(){
    try{
        const respostaServer = await fetch("/requests/foto");
        fotos = await respostaServer.json();
        proxImagem();
    }
    catch (error){
        console.error("Erro no retorno de imagens: ", error) // DEBUG
    }
}

function proxImagem(){
    if (indexAtual < fotos.length) {
        const imageOutput = document.getElementById("imageOutput")
        imageOutput.src = fotos[indexAtual].img;
        console.log(`Current image: ${imageOutput.src}`); // DEBUG
    }
    else{
        showall_message()
    }
}

function showall_message(){
    const imageContainer = document.getElementById("imageContainer-box");

    imageContainer.innerHTML = "";

    const button = document.createElement("button");
    button.textContent = "Go to next page";
    button.onclick = function(){
        window.location.href = "/feed-all";
    }

    imageContainer.appendChild(button);
    console.log("botão criado") // DEBUG
}
// DOMCONTENTLOADED é necessário para interpretar os movimentos de mouse, se não houvesse, só funcionaria no mobile com gestos de touch
document.addEventListener("DOMContentLoaded", () =>
{
    const imageContainer = document.getElementById("imageContainer-box");
    const hammer = new Hammer(imageContainer);
    // inicializando o hammer
    // nessas duas funções, a lib hammer controla os gestos feitos com o mouse
    hammer.on("swipeleft", () =>
        {console.log("Swiped left");
        update_counter("dislike")
        indexAtual += 1; // proxima imagem
        proxImagem();
    })

    hammer.on("swiperight", () =>{
        console.log("Swiped right");
        update_counter("like")
        indexAtual += 1;
        proxImagem();
    })
})

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




