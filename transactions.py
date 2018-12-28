from Models import *
from sqlobject import OR, AND, LIKE
import hashlib

def create_user(username, email, password):
    try:

        check = User.select(OR(User.q.username == username, User.q.email == email))
        
        print (check.count())
        if check.count() > 0:
            return "invalid"

        h = hashlib.md5()
        h.update(password.encode())
        User(username=username,
             email=email,
             password=h.hexdigest()
            )
        return "ok"

    except Exception as e:
        print(e)
        return "failed"


def check_username_password(username, password):
    try:
        h = hashlib.md5()
        h.update(password.encode())

        select = User.select(AND(User.q.username == username, User.q.password == h.hexdigest()))
        select.getOne()

        return "ok"
    except Exception as e:
        print(e)
        return "failed!"

def search_users(username, search_user):
    try:
        result = []
        select = User.select(LIKE(User.q.username, "%{}%".format(search_user)))
        
        # print(123)
        select_for_con = UserContacts.select(UserContacts.q.user == User.select(User.q.username == username).getOne())

        # print (dir(select_for_con))
        # for i in select_for_con:
        #     print(i)
        #     print(type(i))
        #     print(i.user)
        
        for i in select:
            flag = False 
            for j in select_for_con:
                print(j.con_user.username)
                if j.con_user.username == i.username:
                    flag = True
                    break
            if flag:
                continue
            result.append(i.username)
        
        return result
    except Exception as e:
        print(e)
        return "failed"


def add_contacts(username, contact):
    try:
        user = User.select(User.q.username == username).getOne()
        contact_user = User.select(User.q.username == contact).getOne()

        UserContacts(user=user, con_user=contact_user)
        
        return "ok"
    except Exception as e:
        print(e)
        return "failed"


def get_contacts_by_username(username):
    try:
        user = User.select(User.q.username == username).getOne()
        user_contacts = UserContacts.select(UserContacts.q.user == user)
        result = []
        for i in user_contacts:
            temp = {"status":True}
            temp['user']=i.con_user
            result.append(temp)
        
        return result
    except Exception as e:
        print(e)
        return []

def create_room(username, room_name):
    try:
        user = User.select(User.q.username == username).getOne()
        room = Room(admin=user, name=room_name, numbers=1)
        RoomUsers(room=room, users=user)

        return 'ok', room
    except Exception as e:
        print(e)
        return "failed", None


def get_rooms(username):
    try:
        
        user = User.select(User.q.username == username).getOne()
        room_users = RoomUsers.select(RoomUsers.q.users == user)

        result = list(room_users)
        return result

    except Exception as e:
        print(e)
        return []

def get_room_by_id(room_id):
    try: 
        room = Room.select(Room.q.id == room_id).getOne()
        return room
    except Exception as e:
        print(e)
        return 'failed'


def check_user_in_room(username, room_id):
    try:
        user = User.select(User.q.username == username).getOne()
        room = Room.select(Room.q.id == room_id).getOne()
        RoomUsers.select(AND(RoomUsers.q.users == user, RoomUsers.q.room == room)).getOne()
        
        return 'ok'

    except Exception as e:
        print(e)
        return 404
    

def get_contacts_of_room(room_id):
    try:
        room = Room.select(Room.q.id == room_id).getOne()
        room_users = RoomUsers.select(RoomUsers.q.room == room)
        # for i in room_users:
            # print(i)
        return list(room_users)

    except Exception as e:
        print(e)
        return []


def add_to_room(room_id, username):
    try:
        if check_user_in_room(username, room_id) == 'ok':
            
            return 'already'

        room = Room.select(Room.q.id == room_id).getOne()
        user = User.select(User.q.username == username).getOne()

        RoomUsers(room=room, users=user)

        return 'ok'

    except Exception as e:
        print(e)
        return 'failed'