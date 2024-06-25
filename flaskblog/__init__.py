from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Intializes the hashing class by instantiating the variable bcrypt
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login' #if login_required is activated then this page is displayed
login_manager.login_message_category = 'info' # messages regarding login required are set to display flash messages in the color blue

from flaskblog import routes