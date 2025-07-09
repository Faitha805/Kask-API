from flask import Flask
from app.extensions import db, migrate, jwt
from app.controllers.auth.auth_controller import auth

def create_app():
    # Application factory function
    app = Flask(__name__)
    # Registering the config class within the factory function.
    app.config.from_object('config.Config')

    # Initialization of the app instance
    db.init_app(app)

    # initializing the migrate app and db instance
    migrate.init_app(app, db)

    # Initializing the jwt object in the app.
    jwt.init_app(app)

    # importing and registering models
    from app.models.users import User
    from app.models.services import Service
    from app.models.gallery import Gallery
    from app.models.bookings import Booking
    from app.models.payments import Payment

    # Registering blueprints
    # auth blueprint
    app.register_blueprint(auth)

    @app.route("/")
    def home():
        return "Kask API Setup"

    return app