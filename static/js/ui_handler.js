function send_click() {
    console.log("salam");
    let a = document.getElementsByName("chatbox");
    a.forEach(i => i.classList.remove('hide'))
}