from flask import Flask
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

@app.route('/')
def hello_world():
    return 'Hello, World! This is naebak-admin-service.'

if __name__ == '__main__':
    app.run()

