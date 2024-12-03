const cadastrarBtn = document.getElementById('cadastrar');
const loginBtn = document.getElementById('logIn');
const container = document.getElementById('container');

cadastrarBtn.addEventListener('click', () =>{
    container.classList.add("right-panel-active");
}); // muda o estado do container, ativando uma animação de delizar

loginBtn.addEventListener('click', () =>{
    container.classList.remove("right-panel-active");
}); // o contrário, reverte a animação, voltando ao default