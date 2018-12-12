from sqlobject import StringCol, SQLObject, ForeignKey, sqlhub, connectionForURI, UnicodeCol
from config import DB_DIR

sqlhub.processConnection = connectionForURI("sqlite:" + DB_DIR)


class User(SQLObject):
    username = UnicodeCol()
    email = UnicodeCol()
    password = UnicodeCol()
    

class Room(SQLObject):
    admin = ForeignKey('User')

class RoomUsers(SQLObject):
    room = ForeignKey('Room')
    users = ForeignKey('User')

class UserContacts(SQLObject):
    user = ForeignKey('User')
    con_user = ForeignKey('User')


if __name__ == '__main__':
    User.createTable()
    Room.createTable()
    RoomUsers.createTable()
    UserContacts.createTable()