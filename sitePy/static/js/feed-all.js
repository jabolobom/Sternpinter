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
