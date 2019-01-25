function send_click(evnet) {
    console.log("salam");
    document.querySelector("#user_id").value = event.target.parentElement.parentElement.id;
    console.log(document.querySelector("#user_id").value);

    let chatbox = document.getElementsByName("chatbox");
    let collection_chatbox = document.getElementsByName("collection_chatbox");
    chatbox.forEach(i => i.classList.remove('hide'));
    collection_chatbox.forEach(i => i.classList.remove('hide'));
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
                        <a href="#!"  onclick="send_click()">
                        <i class="material-icons">send</i></a>`;
        document.querySelector("#online_contact_list").appendChild(li);

    })
}