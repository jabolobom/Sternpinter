let fotos = [];
let indexAtual = 0;

async function recebeFoto(){
    try{
        const respostaServer = await fetch("/requests/foto");
        fotos = await respostaServer.json();
        proxImagem();
    }
    catch (error){
        console.error("Erro no retorno de imagens: ", error)
    }
}

function proxImagem(){
    if (indexAtual < fotos.length) {
        const imageOutput = document.getElementById("imageOutput")
        imageOutput.src = fotos[indexAtual].img;
        console.log(`Current image: ${imageOutput.src}`);
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
    console.log("botão criado")
}

document.addEventListener("DOMContentLoaded", () =>
{
    const imageContainer = document.getElementById("imageContainer-box");
    const hammer = new Hammer(imageContainer);
    // inicializando o hammer

    hammer.on("swipeleft", () =>
        {console.log("Swiped left");
        indexAtual += 1;
        proxImagem();
    })

    hammer.on("swiperight", () =>{
        console.log("Swiped right");
        indexAtual += 1;
        proxImagem();
    })
})

recebeFoto();
console.log(fotos);
