from flask import Flask 
from .models import User
from .extensions import db
import os

DEV = False

def create_app():
        
    app = Flask(__name__, static_folder='../react/build/static',
                template_folder='../react/build')

    app.config['SQLALCHEMY_TRACK_MODIFIATIONS'] = False
    if DEV:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
        app.debug = True
    else:
        app.config['DATABASE_URI'] = os.environ.get('DATABASE_URL')
        app.debug = False
    db.init_app(app)
    
    with app.app_context():
        
        from . import routes

        # db.drop_all()
        db.create_all()


        app.run()