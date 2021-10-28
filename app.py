from google.cloud import datastore
from flask import Flask
import boat

# REST API by Eric Chiu

app = Flask(__name__)
app.register_blueprint(boat.bp)

@app.route('/')
def index():
    return "Please navigate to /boats to use this API"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)