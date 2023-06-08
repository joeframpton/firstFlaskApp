from flask import Flask
from .extensions import db, login_manager
from .admin.routes import admin
from .public.routes import public



def create_app():
    app = Flask (__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 0 #MYSQL URI GOES HERE
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    

    app.config['SECRET_KEY'] = 0 #SECRET KEY GOES HERE

    app.config['RECAPTCHA_PUBLIC_KEY'] = 0 #RECAPTCHA KEYS GO HERE
    app.config['RECAPTCHA_PRIVATE_KEY'] = 0 #RECAPTCHA KEYS GO HERE
    app.config['RECAPTCHA_USE_SSL'] = False

    app.config['REMEMBER_COOKIE_SECURE'] = True

    
    db.init_app(app)

    app.register_blueprint(admin)
    app.register_blueprint(public)

    login_manager.init_app(app)   

    return app