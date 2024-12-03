const dangerButton = document.getElementById("dangerbutton");
const modal = document.getElementById("modalbox");
const confirmButton = document.getElementById("confirmar_delete");
const cancelButton = document.getElementById("cancelar_delete");
// recebe elementos como variaveis para poder colocar os event listeners
dangerButton.addEventListener("click", () =>{
    modal.style.display = "block";
})
// faz o modal aparecer com um click no botão de danger
cancelButton.addEventListener("click", () =>{
    modal.style.display = "none";
})
// e desaparecer com um click no botão de cancelar
confirmButton.addEventListener("click", async () => {
    modal.style.display = "none";
    // ao confirmar o delete, ele esconde o modal
    const csrfToken = document.querySelector('meta[name="csrf_token"]').getAttribute('content');
    // coloca o csrf token numa variável para enviar junto do JSON no request api
    // impede que qualquer um só coloque o link e delete sua conta
    try {
        const response = await fetch('/delete_account_call', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": csrfToken
            },
        });
        // se conecta a rota de deletar a conta, o resto é gerenciado pela função de deletar
        if (response.ok) {
            alert("Conta deletada com sucesso!");
            window.location.href = "/";
        } else {
            alert("ERRO ao deletar conta.");
        }
    } catch (error) {
        alert("ERRO ao se conectar ao servidor.");
        console.error(error);
    }
});