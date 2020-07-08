from flask import Flask 
from .models import User
from .extensions import db
import os

DEV = False

def create_app():
        
    app = Flask(__name__, static_folder='../build/static',
                template_folder='../build')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if DEV:
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pocketgan.db"
        app.debug = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        app.debug = False
    db.init_app(app)
    
    with app.app_context():
        
        from . import routes

        # db.drop_all()
        db.create_all()

        return app
        # app.run()
