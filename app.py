from flask import Flask, session, render_template, redirect, url_for, request, Response, jsonify
from flask_socketio import SocketIO, emit
from flask_socketio import join_room as join_room_online
from flask_socketio import close_room as close_room_online
from config import SECRET, CONNECTION_EXPIRE_TIME
import gevent
from gevent.pywsgi import WSGIServer
from gevent.queue import Queue
import werkzeug.serving
import json
import time
import transactions


class ServerSentEvent(object):

    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (self.desc_map[k], k) for k in self.desc_map if k]

        return "%s\n\n" % "\n".join(lines)


app = Flask(__name__)
app.secret_key = SECRET
subscriptions = []

ServerRooms = {}
socket_io = SocketIO(app)

online_users = {}

@app.route("/old_login")
def test():
    return render_template("home.html")


@app.route("/")
def home():
    if 'username' not in session:
        return render_template("new_login.html")

    # contacts = transactions.get_contacts(session['username'])
    rooms = transactions.get_rooms(session['username'])

    # rooms = []
    return render_template("new_home.html", username=session['username'], rooms=rooms)


@app.route('/signup')
def signup():
    if 'username' not in session:
        return render_template('signup.html')
    else:
        return redirect(url_for('home'))


@app.route("/login", methods=['POST'])
def login():
    if request.method != 'POST':
        return 'invalid method!'

    form = request.form
    username = form['username']
    password = form['passw']

    # check username and password
    stat = transactions.check_username_password(username, password)
    if stat == "ok":
        session['username'] = username
        return redirect(url_for('home'))
    return stat


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method != 'POST':
        return 'invalid method!'

    form = request.form
    password = form['passw']

    if password != form['repassw']:
        return 'invalid pass'

    username = form['username']
    email = form['email']

    # register user in db
    stat = transactions.create_user(username, email, password)
    if stat == "ok":
        print("OK")
        # session['username'] = username
        return jsonify({"status": "OK"})
        # return redirect(url_for('home'))
    else:
        print(stat)
        return stat

    return "failed"


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('home'))


@app.route('/search_user')
def search_user():
    if request.method != 'GET':
        return "invalid method!"

    if 'username' not in session:
        return redirect(url_for('home'))

    if 'username' not in request.args:
        return "invalid input"

    search_user = request.args['username']
    stat = transactions.search_users(session['username'], search_user)
    if stat != 'failed' and stat:
        if session['username'] in stat:
            stat.remove(session['username'])
        return render_template('add_contact.html', users=stat)

    return "failed"


@app.route("/add_con/<username>")
def add_contact(username):
    if 'username' not in session:
        return redirect(url_for('home'))

    if session['username'] == username:
        return "can not add yourself to your contacts."

    # add to contacts
    return transactions.add_contacts(session['username'], username)


# wrong
@app.route("/create_room", methods=['POST'])
def create_room():
    if 'username' not in session:
        return redirect(url_for('home'))

    if request.method != 'POST':
        return 'invalid method'

    form = request.form
    if 'room_name' not in form:
        return 'invalid input'

    return transactions.create_room(session['username'], form['room_name'])


# wrong
@app.route('/room/<room_id>')
def room(room_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']

    if transactions.check_user_in_room(username, room_id) != 'ok':
        return 'this room is not for you!'

    room_users = transactions.get_contacts_of_room(room_id)

    contacts = transactions.get_contacts_by_username(username)

    for i in contacts:
        pass

    return render_template('room.html', contacts=contacts, room=room_id, room_users=room_users)


# wrong
@app.route('/add_to_room/<room_id>/<username>')
def add_to_room(room_id, username):
    if 'username' not in session:
        return redirect(url_for('home'))

    stat = transactions.add_to_room(room_id, username)

    return redirect(url_for('room', room_id=room_id))


@app.route('/create_room/wait/<room_name>')
def render_new_room(room_name):
    if 'username' not in session:
        return redirect(url_for('home'))

    stat, room = transactions.create_room(session['username'], room_name)
    if stat == 'ok':
        return render_template('new_room.html', room=room)
    return 'failed'


@app.route('/create_room/wait', methods=["POST"])
def render_new_room_form():
    if 'username' not in session:
        return redirect(url_for('home'))

    if 'room_name' not in request.form:
        return 'invalid input'

    stat, room = transactions.create_room(session['username'], request.form['room_name'])
    if stat == 'ok':
        return render_template('new_room.html', room=room)
    return 'failed'


@app.route('/listen_to_room/<room_id>')
def listen_to_room(room_id):
    def gen():
        q = Queue()
        # print(ServerRooms.get(room_id, []), type(ServerRooms.get(room_id, [])))
        if ServerRooms.get(room_id, False):
            ServerRooms[room_id].append(q)
        else:
            ServerRooms[room_id] = [q]

        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except Exception as e:  # Or maybe use flask signals
            print(e)
            ServerRooms.pop(room_id, None)

    return Response(gen(), mimetype="text/event-stream")


@app.route('/join/<room_id>')
def join_room(room_id):
    def notify():
        # msg = str("salam\nmy ip: \nmy address: \n")
        msg = {"message": 'salam',
               "ip": "x.x.x.x",
               "address": "address"}
        # for sub in subscriptions[:]:
        #     sub.put(msg)
        # print(ServerRooms)
        # print(ServerRooms[room_id])
        for i in ServerRooms[room_id]:
            # print(msg)
            i.put(json.dumps(msg))

    gevent.spawn(notify)

    room = transactions.get_room_by_id(room_id)

    return render_template('new_room.html', room=room)


@app.route('/join', methods=["POST"])
def join_to_room():
    if 'username' not in session:
        return redirect(url_for('home'))

    if 'room_id' not in request.form:
        return 'invalid input'

    def notify(room_id):
        msg = {"message": 'salam',
               "ip": "x.x.x.x",
               "address": "address"}
        # for sub in subscriptions[:]:
        #     sub.put(msg)
        # print(ServerRooms)
        # print(ServerRooms[request.form['room_id']])
        for i in ServerRooms[room_id]:
            # print(msg)
            i.put(json.dumps(msg))

    gevent.spawn(notify, room_id=request.form['room_id'])

    room = transactions.get_room_by_id(request.form['room_id'])

    return render_template('new_room.html', room=room)


@app.route("/test_sse_send")
def test_sse_send():
    # Dummy data - pick up from request for real data
    def notify():
        msg = str(time.time())
        for sub in subscriptions[:]:
            sub.put(msg)

    gevent.spawn(notify)

    return "OK"


@app.route("/test_sse_subscribe")
def test_sse_subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit:  # Or maybe use flask signals
            subscriptions.remove(q)

    print(subscriptions)

    return Response(gen(), mimetype="text/event-stream")

@app.route("/websocket")
def temp_api():
    return render_template('websocket_temp.html')


@socket_io.on('message')
def handle_incomming_message(message):
    print('Receive message: ', message)


@socket_io.on('my_ping', namespace='/ws')
def ping_pong():
    emit('my_pong')


@socket_io.on('connect', namespace='/ws')
def on_connection():
    if 'username' in session:
        contacts = transactions.get_contacts_by_username(session['username'])
        join_room_online(session['username'])
        online_users[session['username']] = [time.time(), CONNECTION_EXPIRE_TIME, contacts]
        temp = []
        for con in contacts:
            if con in online_users:
                temp.append(con)
        
        emit('on_con_resp', {'response': 'online_contacts', 
                            'online_contacts': temp})
        
        # send a message to corresponding user's contacts
        for user in online_users:
            if session['username'] in online_users[user][2]:
                temp = []
                for con in online_users[user][2]:
                    if con in online_users:
                        temp.append(con)

                emit('on_con_resp', {'response': 'online_contacts',
                                    'online_contacts': temp}, room=user)

    print('receive a connection')


@socket_io.on('disconnect', namespace='/ws')
def on_disconnection():
    if 'username' in session:
        online_users.pop(session['username'], False)
        close_room_online(session['username'])

        # send a message to corresponding user's contacts
        for user in online_users:
            if session['username'] in online_users[user][2]:
                temp = []
                for con in online_users[user][2]:
                    if con in online_users:
                        temp.append(con)
                emit('on_con_resp', {'response': 'online_contacts',
                                    'online_contacts': temp}, room=user)

        print("session: %s disconnected!" % session['username'])
    print('clinet disconnected')


@socket_io.on("chat", namespace='/ws')
def on_chat(message):
    if 'username' in session:
        room = message['user_id']
        message = message['message']

        emit('on_new_mess', {'response': 'new_message',
                            'from': session['username'], 
                            'message': message}, room=room)


def background_task():
    while True:
        to_be_deleted = []
        for user in online_users:
            online_users[user][0] += 1
            flag = online_users[user][0] >= CONNECTION_EXPIRE_TIME
            if flag:
                to_be_deleted.append(user)
                # send to other contacts that user is offline
        time.sleep(1)


@werkzeug.serving.run_with_reloader
def run_server():
    app.debug = True
    server = WSGIServer(("0.0.0.0", 5000), app)
    server.serve_forever()

@werkzeug.serving.run_with_reloader
def run_with_socketio():
    socket_io.debug = True
    server = WSGIServer(("0.0.0.0", 5000), socket_io)
    server.serve_forever()


if __name__ == "__main__":
    # run_server()
    run_with_socketio()
    # app.run()
