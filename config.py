import os

DB_DIR = os.path.abspath(os.curdir) + "/database.db"
SECRET = "some random string"
CONNECTION_EXPIRE_TIME = 10 * 60 # seconds