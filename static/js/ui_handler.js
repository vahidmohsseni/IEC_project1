function send_click(e) {
    e = e || window.event;
    let username = e.target.parentElement.parentElement.id;
    document.querySelector("#user_id").value = username;
    document.querySelector("#chatbox_title").innerHTML = username;
    console.log(document.querySelector("#user_id").value);

    let chatbox = document.getElementsByName("chatbox");
    let collection_chatbox = document.getElementsByName("collection_chatbox");
    chatbox.forEach(i => i.classList.remove('hide'));
    collection_chatbox.forEach(i => i.classList.remove('hide'));
    document.getElementsByName("menu_box")[0].classList.add('hide');
}

function close_click(event) {
    let chatbox = document.getElementsByName("chatbox");
    chatbox.forEach(i => i.classList.add('hide'));
    document.getElementsByName("menu_box")[0].classList.remove('hide');
}

function add_online_user(online_users) {
    online_users.forEach(name => {
        document.querySelector(`#${name}`).remove();
        let li = document.createElement("li");
        li.classList.add(`collection-item`);
        li.classList.add("avatar");
        li.id = name;
        li.innerHTML = `<img src="/static/img_avatar2.png" alt="" class="circle">
                        <span class="title">${name}</span>
                        <br>
                        <a href="#!"  onclick="send_click(event)">
                        <i class="material-icons">send</i></a>`;
        document.querySelector("#online_contact_list").appendChild(li);

    })
}

function add_chat(chat, sender) {
    let chat_window = document.querySelector("#chat_window");
    let div = document.createElement("div");
    if (sender === 1)
        div.setAttribute("class", "chip cyan darken-2 white-text text");
    else
        div.setAttribute("class", "chip white cyan-text text-darken-2 right");
    div.innerHTML = chat;
    chat_window.appendChild(div);
    chat_window.appendChild(document.createElement("br"));
    chat_window.appendChild(document.createElement("br"));
}