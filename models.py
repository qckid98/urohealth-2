from flask_login import UserMixin
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from database import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON
import os

# from sqlalchemy import Column, Integer, String
# from app import db

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'database.db')

engine = create_engine("sqlite:///" + db_path, echo=True)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()

# Set your classes here.
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    
    # Relasi ke Assessment
    assessments = db.relationship('Assessment', backref='author', lazy=True)

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User {self.name}>'
    
class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Pastikan nama tabel user adalah 'users'
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Menyimpan jawaban kuesioner (Hematuria, Nyeri, dll) dalam format JSON agar fleksibel
    answers = db.Column(db.JSON, nullable=False)
    
    # Hasil Analisis
    total_score = db.Column(db.Integer, default=0)
    total_score_kh = db.Column(db.Integer, default=0)
    risk_level = db.Column(db.String(50))
    ai_advice = db.Column(db.Text)

    def __repr__(self):
        return f"Assessment('{self.date_posted}', '{self.total_score}')"

"""
class User(Base):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(30))

    def __init__(self, name=None, password=None):
        self.name = name
        self.password = password
"""

# Create tables.
Base.metadata.create_all(bind=engine)
