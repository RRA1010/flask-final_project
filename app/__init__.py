from flask import Flask

app = Flask(__name__)

# to avoid circular imports
from app import routes