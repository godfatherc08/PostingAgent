from flask import Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy



def create_app():
    app = Flask(__name__)

    load_dotenv()

    from .views import views

    app.register_blueprint(views, url_prefix="/")


    return app
