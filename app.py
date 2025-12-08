from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from markupsafe import escape # HTML escaping # 

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root' #temp
app.config['MYSQL_DB'] = 'running_shoe_db'

mysql = MySQL(app)

# model section



# routes/urls eq djngo
@app.route('/')
def home():
    return "Hello, Flask!"

# run app.py for debugging
if __name__ == "__main__":
    app.run(debug=True)

#md5 (128 bit)