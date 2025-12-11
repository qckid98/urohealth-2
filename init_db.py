# FILE: init_db.py
from app import app
from database import db
from models import User, Assessment

if __name__ == '__main__':
    with app.app_context():
        print("Sedang membuat tabel database...")
        db.create_all()
        print("Berhasil! File 'urologi.db' kini berisi tabel Users dan Assessments.")