import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask - set SECRET_KEY in the environment for any real deployment
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "business.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads (one workbook per user)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"xlsx", "xlsm", "csv"}
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024   # 25 MB

    SAMPLE_FILE = os.path.join(BASE_DIR, "sample_data", "WideLens_Nagpur_Sample.xlsx")
