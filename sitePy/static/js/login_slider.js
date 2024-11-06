const cadastrarBtn = document.getElementById('cadastrar');
const loginBtn = document.getElementById('logIn');
const container = document.getElementById('container');

cadastrarBtn.addEventListener('click', () =>{
    container.classList.add("right-panel-active");
});

loginBtn.addEventListener('click', () =>{
    container.classList.remove("right-panel-active");
});