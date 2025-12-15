"""Application factory for the running shoe API."""

import os

from flask import Flask
from flask_mysqldb import MySQL


mysql = MySQL()


def create_app() -> Flask:
	app = Flask(__name__)

	app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
	app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
	app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'root')
	app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'running_shoe_db')
	app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
	app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
	app.config['JWT_EXPIRATION_DELTA'] = int(os.getenv('JWT_EXPIRATION_DELTA', '60'))

	mysql.init_app(app)
	app.extensions['mysql'] = mysql

	from app.routes import bp

	app.register_blueprint(bp)

	return app


app = create_app()