from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'temp_db'

mysql = MySQL(app)

# run app.py for debugging
if __name__ == "__main__":
    app.run(debug=True)