import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    SECRET_KEY = "your-secret-key-change-this"

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "business.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload Folder
    UPLOAD_FOLDER = "uploads"

    # Allowed Extensions
    ALLOWED_EXTENSIONS = {"csv"}