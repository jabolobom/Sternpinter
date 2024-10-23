window.addEventListener('scroll', function() {
    const scrollPercentage = window.scrollY / (document.body.scrollHeight - window.innerHeight);
    const newColor = `rgb(${scrollPercentage * 255}, ${scrollPercentage * 100}, 150)`;
    document.body.style.backgroundColor = newColor;
    console.log("working")
});