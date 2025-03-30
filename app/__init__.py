from flask import Flask

from .bundles import bundles, register_bundles
from .extensions import db, migrate, login_manager, assets
from .config import Config

from .routes.application import application
from .routes.disinfection import disinfection
from .routes.dashboard import dashboard
from .routes.user import user
from .signals import register_signals
from .functions import initial_data



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(application)
    app.register_blueprint(disinfection)
    app.register_blueprint(dashboard)
    app.register_blueprint(user)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    assets.init_app(app)
    
    # LOGIN MANAGER
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Вы не можете получить доступ к данной странице. Нужно сначала войти.'
    login_manager.login_message_category = 'info'

    # ASSETS
    register_bundles(assets, bundles)
    
    # SIGNALS
    register_signals(app)

    with app.app_context():
        db.create_all()
        initial_data()

    return app
