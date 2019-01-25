let ws = new WebSocket("ws://127.0.0.1:5000/connect");
ws.onopen = function () {
    ws.send(JSON.stringify({type: "echo", payload: "hi!"}));
};
ws.onclose = function (evt) {
    console.log("socket closed");
};
ws.onmessage = function (evt) {

    let msg = JSON.parse(evt.data);
    if (msg.status === "ok") {
        let online_users = msg.online_users;
        add_online_user(online_users);
        console.log(online_users);
    }
    console.log(msg);
};

function send_mess(event) {
    ws.send(JSON.stringify({
        type: "chat", payload: {
            user_id: document.querySelector('#user_id').value,
            message: document.querySelector('#message').value
        }
    }));
    return false;
};