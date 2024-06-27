from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY' #Save your key as an enviornment variable, i forgot to do it

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Intializes the hashing class by instantiating the variable bcrypt
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login' #if login_required is activated then this page is displayed
login_manager.login_message_category = 'info' # messages regarding login required are set to display flash messages in the color blue

from flaskblog.users.routes import users
from flaskblog.posts.routes import posts
from flaskblog.main.routes import main

app.register_blueprint(users, url_prefix='/user')
app.register_blueprint(posts, url_prefix='/post')
app.register_blueprint(main)
