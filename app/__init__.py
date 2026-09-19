from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config

db = SQLAlchemy()
bcrypt=Bcrypt()
login_manager=LoginManager()
login_manager.login_view='user.login'
login_manager.login_message_category='info'


mail = Mail()


def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	from app.user.routes import user
	from app.posts.routes import posts
	from app.errors.handlers import errors 
	from app.main.routes import main 

	app.register_blueprint(user)
	app.register_blueprint(posts)
	app.register_blueprint(main)
	app.register_blueprint(errors)

	return app
