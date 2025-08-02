from flask import Flask
from flask_mail import Mail
from app.extensions import db, migrate, jwt
from app.controllers.auth.auth_controller import auth
from app.controllers.users.users_controller import users
from app.controllers.bookings.bookings_controller import bookings
from app.controllers.services.services_controller import services
from app.controllers.gallery.gallery_controller import galleries
from app.controllers.messages.messages_controller import messages
from app.controllers.feedbacks.feedback_controller import feedbacks

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

    # initializing the email extensions in the app.
    mail = Mail()
    mail.init_app(app)

    # importing and registering models
    from app.models.feedback import Feedback
    from app.models.users import User
    from app.models.services import Service
    from app.models.gallery import Gallery
    from app.models.bookings import Booking
    from app.models.messages import Message

    # Registering blueprints
    # auth blueprint
    app.register_blueprint(auth)

    # users blueprint
    app.register_blueprint(users)

    # booking blueprint
    app.register_blueprint(bookings)

    # services blueprint
    app.register_blueprint(services)

    # gallery blueprint
    app.register_blueprint(galleries)

    # feedback blueprint
    app.register_blueprint(feedbacks)

    # message blueprint
    app.register_blueprint(messages)

    @app.route("/")
    def home():
        return "Kask API Setup"

    return app