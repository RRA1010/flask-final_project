import os
from flask import render_template, request
from flask_mysqldb import MySQL
from flaskr import create_app
from markupsafe import escape # HTML escaping #


app = create_app()

mysql = MySQL(app)

# model section


# routes/urls eq djngo
@app.route('/')
def home():
    return "Hello, Flask!"

# run app.py for debugging
if __name__ == '__main__':
    app.run(debug=True)

#md5 (128 bit)