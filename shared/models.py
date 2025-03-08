from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from shared.database import db

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    hash = db.Column(db.String(256), nullable=False)
    google_id = db.Column(db.String(30), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime)
    totp_secret = db.Column(db.String(32))
    last_otp_sent = db.Column(db.DateTime)
    password_set = db.Column(db.Boolean, default=False)

    birthdays = db.relationship('Birthdays', backref='user', lazy=True)

    # Flask-Login required properties and methods
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Birthdays(db.Model):
    __tablename__ = 'birthdays'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    birthdates = db.Column(db.String(10), nullable=False)

class AuditLogs(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(80), nullable=False)  # Removed unique constraint
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('Users', backref='audit_logs', lazy=True)

