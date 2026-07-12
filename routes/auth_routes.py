from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from database.database import db, bcrypt
from database.models import User

auth = Blueprint("auth", __name__)


# ----------------------------
# Register
# ----------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        name = request.form.get("name").strip()

        email = request.form.get("email").strip().lower()

        password = request.form.get("password")

        confirm_password = request.form.get("confirm_password")

        # Validation

        if not name or not email or not password or not confirm_password:

            flash("Please fill all fields.", "danger")

            return redirect(url_for("auth.register"))

        if len(password) < 8:

            flash("Password must be at least 8 characters.", "danger")

            return redirect(url_for("auth.register"))

        if password != confirm_password:

            flash("Passwords do not match.", "danger")

            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            flash("Email already registered.", "warning")

            return redirect(url_for("auth.register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ----------------------------
# Login
# ----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email").strip().lower()

        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):

            login_user(user)

            flash("Login Successful!", "success")

            return redirect(url_for("auth.dashboard"))

        flash("Invalid Email or Password.", "danger")

    return render_template("login.html")


# ----------------------------
# Dashboard
# ----------------------------
@auth.route("/dashboard")
@login_required
def dashboard():

    return f"""
    <h2>Welcome {current_user.name}</h2>

    <p>You are successfully logged in.</p>

    <a href='/logout'>Logout</a>
    """


# ----------------------------
# Logout
# ----------------------------
@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "info")

    return redirect(url_for("auth.login"))