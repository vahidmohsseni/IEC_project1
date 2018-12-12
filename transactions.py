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
