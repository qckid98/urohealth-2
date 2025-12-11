# config.py
import os

class Config(object):
    # Kunci rahasia untuk sesi login (wajib ada)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci_rahasia_sangat_aman'

    # Konfigurasi Database SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')

    # Mematikan notifikasi perubahan database (menghemat memori)
    SQLALCHEMY_TRACK_MODIFICATIONS = False