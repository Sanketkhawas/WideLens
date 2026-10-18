import os

from flask import Flask

from config import Config

from database.database import db
from database.database import bcrypt
from database.database import login_manager

# Import Models
from database.models import User

# Import Blueprint
from routes.auth_routes import auth
from routes.upload_routes import upload_bp
from routes.dashboard_routes import dash_bp
from routes.api_routes import api_bp


def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(upload_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(api_bp)

    # Home Route
    @app.route("/")
    def home():
        from flask import render_template
        return render_template("index.html")

    with app.app_context():
        db.create_all()
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host="127.0.0.1",
        port=5000
    )