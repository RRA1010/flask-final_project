import os

from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app(test_config=None):
    #create & config app
    app = Flask(__name__, instance_relative_config=True)
    #set default config
    mysql.init_app(app)
    #mysql
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'root' #temp
    app.config['MYSQL_DB'] = 'running_shoe_db'

    if test_config is None:
        #load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)
    
    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    

    return app