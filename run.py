from flask import Flask

app = Flask(__name__)


from app import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__" :
    app.run()