import os
from datetime import timedelta

# Basic Config
DEBUG = True
SECRET_KEY = os.urandom(24)

# Database Config
# HOSTNAME = '127.0.0.1'
HOSTNAME = 'localhost'
PORT = '3306'
DATABASE = 'Pocket'
USERNAME = 'root'
PASSWORD = 'h1951116'
# authentication_string = 'h1951116'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI
PERMANENT_SESSION_LIFETIME = timedelta(days=15)

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_TEARDOWN = True

# Mail Congig
MAIL_SERVER = 'smtp.163.com'
MAIL_USERNAME = 'pocketcharacter'
MAIL_PASSWORD = 'pocket163'