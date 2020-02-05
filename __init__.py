from datetime import timedelta
from logging.handlers import RotatingFileHandler
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_user import SQLAlchemyAdapter, UserManager


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site_aumai.db?check_same_thread=False'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:aumai123!@mysql:3306/aumaiDB'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CSRF_ENABLE'] = True
    app.config['USER_ENABLE_EMAIL'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('../aumai/logs/aumai.log', maxBytes=1000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.logger.debug('Inizializzo DB')
    db.init_app(app)

    app.logger.debug('Inizializzo Utenti')
    from .models import User
    db_adapter = SQLAlchemyAdapter(db,  User)
    user_manager = UserManager(db_adapter, app)
    user_manager.login_manager.login_view='auth.login'

    app.logger.debug('Inizializzo Auth')
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    app.logger.debug('Inizializzo Main')
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    app.logger.debug('Inizializzo Responsabile')
    from .responsabile import responsabile as responsabile_blueprint
    app.register_blueprint(responsabile_blueprint)

    app.logger.debug('Inizializzo Cassiere')
    from .cassiere import cassiere as cassiere_blueprint
    app.register_blueprint(cassiere_blueprint)

    app.logger.debug('Inizializzo REST_API')
    from .rest_api import rest as rest_blueprint
    app.register_blueprint(rest_blueprint)

    app.logger.debug('Inizializzo Reports')
    from .reports import reports as report_blueprint
    app.register_blueprint(report_blueprint)

    app.logger.debug('Inizializzo Form_Validartor')
    from .form_validator import form_validator as validator_blueprint
    app.register_blueprint(validator_blueprint)

    app.logger.info('Application initialized')

    return app
