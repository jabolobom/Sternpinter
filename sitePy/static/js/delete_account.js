const dangerButton = document.getElementById("dangerbutton");
const modal = document.getElementById("modalbox");
const confirmButton = document.getElementById("confirmar_delete");
const cancelButton = document.getElementById("cancelar_delete");

dangerButton.addEventListener("click", () =>{
    modal.style.display = "block";
})

cancelButton.addEventListener("click", () =>{
    modal.style.display = "none";
})

confirmButton.addEventListener("click", async () => {
    modal.style.display = "none";
    const csrfToken = document.querySelector('meta[name="csrf_token"]').getAttribute('content');

    try {
        const response = await fetch('/delete_account_call', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": csrfToken
            },
        });

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