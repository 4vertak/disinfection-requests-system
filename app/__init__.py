from .domain.services.user_service import UserInitializer
from flask import Flask

from .core.bundles import bundles, register_bundles
from .core.extensions import db, migrate, login_manager, assets
from .core.config import Config

from .routes.application.routes import application
from .routes.disinfection.routes import disinfection
from .routes.dashboard.routes import dashboard
from .routes.user.routes import user

from .core.signals import register_signals



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
        # UserInitializer.initialize_user_id_counter()
        UserInitializer.create_admin_account()
        UserInitializer.fill_directories()

    return app
