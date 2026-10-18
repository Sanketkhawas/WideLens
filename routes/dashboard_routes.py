from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from routes.upload_routes import user_file

dash_bp = Blueprint("dash", __name__)


@dash_bp.route("/app")
@login_required
def index():
    if not user_file(current_user.id):
        return redirect(url_for("upload.upload"))
    return render_template("dashboard.html", user=current_user)
