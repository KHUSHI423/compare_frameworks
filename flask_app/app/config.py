import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-benchmark-key-12345')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///taskboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-benchmark-key-12345')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')