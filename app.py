from flask import Flask

from config import Config

from database.database import db
from database.database import bcrypt
from database.database import login_manager

# Import Models
from database.models import User

# Import Blueprint
from routes.auth_routes import auth


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth)

    # Home Route
    @app.route("/")
    def home():
        return "<h2>WideLens:AI Business Expansion Advisor</h2><p>Application Running Successfully</p>"

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )