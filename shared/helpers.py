import pyotp
from datetime import datetime
from flask import redirect, render_template, url_for, flash
from flask_login import current_user
from flask_mail import Message
from functools import wraps
from shared.models import AuditLogs
from shared.database import db_session as db
from shared.database import get_db


# Temporary OTP storage (use Redis or DB in production)
otps = {}

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def password_set(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("main.login"))
    
        if not current_user.password_set:
            flash("Please set a Password to continue")
            return redirect(url_for("main.add_password"))
        
        return f(*args, **kwargs)

    return decorated_function

def email_confirmed(f):
    """
    Decorate routes to require verification.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("main.login"))
    
        if not current_user.confirmed:
            flash("Account not verified!!")
            return redirect(url_for("main.otp_verification"))
        
        return f(*args, **kwargs)

    return decorated_function


# calculate the age of a friend
def calculate_age(birthdate) ->int: #Take an input birthdate and then output(->) an integer

    #check to see if date format is a date or datetime and if not formats in year-month-day
    if isinstance(birthdate, str): #
        birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
    
    today = datetime.today()
    age = today.year - birthdate.year

    # check if the friend has already celebrated his birthday for the year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    return age
#log users action
def log(action):
    db = get_db()
    user_log = AuditLogs(user_id=current_user.id, action=action, timestamp=datetime.now())
    db.add(user_log)
    db.commit()

#convert to python date.
def date_convert(date):
    return datetime.strptime(date, '%Y-%m-%d').date()

def generate_potp_secret_key():
    return pyotp.random_base32()


def generate_otp_code(potp_secret_key):
    totp = pyotp.TOTP(potp_secret_key, interval=600)
    return totp.now()


def verify_otp_code(potp_secret_key, otp_code):
    totp = pyotp.TOTP(potp_secret_key, interval=600)
    return totp.verify(otp_code)


def send_otp_email(receipient_email, otp_code):
    from app import mail
    msg = Message(
        subject="Your One-Time Password (OTP). ",
        recipients=[receipient_email],
        body=f"Your OTP is: {otp_code}\nThis code is valid for 60 seconds."
    )
    mail.send(msg)
    

def verification_email(user):
    db = get_db()
    if not user.totp_secret:
        user.totp_secret = generate_potp_secret_key()

    user.last_otp_sent = datetime.now()
    db.commit()
    
    otp = generate_otp_code(user.totp_secret)

    try:
        send_otp_email(user.email, otp)
        flash(f"Verification code sent to your email {user.email}. ")
        log(f"otp_email_{(user.email)}")
    except Exception as e:
        flash(f"Failed to send OTP: {str(e)}!")
        log("otp_email_failure")