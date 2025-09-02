from flask import Flask
from agents.core import DatahouseAgent

app = Flask(__name__)
datahouse_agent = DatahouseAgent()

@app.route("/datahouse")
def connect_to_agent():
    return "CONNECT"