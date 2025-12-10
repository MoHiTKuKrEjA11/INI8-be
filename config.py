import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Example: postgresql://username:password@localhost:5432/documents_db
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:alpha123@localhost:5432/documents_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit; adjust as needed
    ALLOWED_EXTENSIONS = {"pdf"}
