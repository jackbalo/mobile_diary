import requests
import pyotp

from flask import jsonify, request, session, abort, Blueprint, url_for
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from shared.models import Users, Birthdays
from shared.database import get_db
from shared.helpers import log, calculate_age, date_convert, password_set, verify_otp_code, generate_potp_secret_key, email_confirmed, verification_email

from sqlalchemy.sql import func

main = Blueprint('main', __name__)
POTP_SECRET_KEY = pyotp.random_base32()

@main.route("/")
def index():
    return jsonify({"message": "Welcome to the Mobile Diary API!"})

@main.route("/api/register", methods=["POST"])
def register():
    db = get_db()
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    phone = data.get("phone")
    dob = data.get("dob")
    name = data.get("name")
    password = data.get("password")
    confirmation = data.get("confirmation")
    hash = generate_password_hash(password, method='pbkdf2:sha256:600000', salt_length=16)
        
    if not username or not password or not email or not phone or not name:
        return jsonify({"error": "All fields are required!"}), 400
    
    if password != confirmation:
        return jsonify({"error": "Password mismatch!"}), 400
    
    try:
        user = Users(name=name, username=username, hash=hash, dob=dob, email=email, phone=phone, password_set=True, totp_secret=generate_potp_secret_key())
        db.add(user)
        db.commit()

        login_user(user)
        log("register")

    except ValueError:
        db.rollback()
        return jsonify({"error": "Username already exists!"}), 403
    
    verification_email(current_user)
    return jsonify({"message": "User registered successfully!"}), 201

@main.route("/api/otp_verification", methods=["POST"])
@login_required
@password_set
def otp_verification():
    db = get_db()
    data = request.get_json()
    if 'resend_otp' in data:
        time_last_otp_sent = None
        if current_user.last_otp_sent: 
            time_last_otp_sent = (datetime.now() - current_user.last_otp_sent).total_seconds()  
            if time_last_otp_sent and time_last_otp_sent < 60:
                return jsonify({"error": f"Resend otp in {60 - int(time_last_otp_sent)} seconds!"}), 400
            else:
                verification_email(current_user)
            return jsonify({"message": "OTP resent successfully!"}), 200
        else:
            verification_email(current_user)
        return jsonify({"message": "OTP resent successfully!"}), 200
    else:
        otp = data.get("otp")
        if not otp:
            return jsonify({"error": "Please enter OTP!"}), 400
        
        if verify_otp_code(current_user.totp_secret, otp):
            current_user.confirmed = True
            current_user.confirmed_on = datetime.now()
            db.commit()
            log("otp_verified")
            return jsonify({"message": "OTP verification successful!"}), 200
        else: 
            log("OTP_verification_failed!")
            return jsonify({"error": "Invalid or expired OTP!"}), 400

@main.route("/api/add_password", methods=["POST"])
@login_required
def add_password():
    db = get_db()
    if current_user.password_set:
        return jsonify({"error": "Password already set!"}), 400

    data = request.get_json()
    password = data.get("password")
    confirmation = data.get("confirmation")
    
    if not password or not confirmation:
        return jsonify({"error": "All fields are required!"}), 400
    
    if password != confirmation:
        return jsonify({"error": "Password mismatch!"}), 400
    
    current_user.hash = generate_password_hash(password, method='pbkdf2:sha256:600000', salt_length=16)
    current_user.password_set = True
    db.commit()

    log("google_register")

    if not current_user.confirmed:
        verification_email(current_user)
        return jsonify({"message": "Password set successfully! OTP sent for verification."}), 200
    
    return jsonify({"message": "Password set successfully!"}), 200

@main.route("/api/login", methods=["POST"])
def login():
    db = get_db()
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Must provide username and password!"}), 400

    user = Users.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Invalid username"}), 403
    if not check_password_hash(user.hash, password):
        return jsonify({"error": "Invalid password!"}), 403

    login_user(user)

    log("log_in")

    if not current_user.confirmed:
        verification_email(current_user)
        return jsonify({"message": "Password set successfully! OTP sent for verification."}), 200
    
    return jsonify({
        "message": "Login successful!", 
        "email_confirmed": user.confirmed
    }), 200

@main.route("/api/signin-google")
def googleCallback():
    db = get_db()
    from app import oauth_client
    try:
        token = oauth_client.myApp.authorize_access_token()

        personDataUrl = "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays"

        headers = {'Authorization': f'Bearer {token["access_token"]}'}
        response = requests.get(personDataUrl, headers=headers)
        person_info = response.json()

        email = token["userinfo"]["email"]
        name = token["userinfo"]["name"]
        google_id = token["userinfo"]["sub"]
        
        birthday = None
        if "birthdays" in person_info and len(person_info["birthdays"]) > 1:
            date_info = person_info["birthdays"][1].get("date", {})
            day = date_info.get("day")
            month = date_info.get("month")
            year = date_info.get("year")
            birthday = f"{year}-{month:02d}-{day:02d}" if year else f"{month:02d}-{day:02d}"

        user = Users.query.filter_by(email=email).first()
        if not user:
            user = Users(name=name, username=name, dob=birthday, email=email, google_id=google_id, totp_secret=generate_potp_secret_key(), last_otp_sent=datetime.now())
            db.add(user)
            db.commit()

        login_user(user)

        if not user.password_set:
            return jsonify({"message": "Password not set!"}), 400
        
        if not user.confirmed:
            verification_email(current_user)
            return jsonify({"message": "OTP sent for verification!"}), 200
                
        log(f"google_login_{name}")
        return jsonify({"message": "Google login successful!"}), 200

    except ValueError:
        db.rollback()
        return jsonify({"error": "Unauthorized login!"}), 403

@main.route("/api/google-login")
def googleLogin():
    from app import oauth_client
    if current_user.is_authenticated:
        abort(404)
    return oauth_client.myApp.authorize_redirect(redirect_uri=url_for("main.googleCallback", _external=True))

@main.route("/api/home")
@login_required
@password_set
@email_confirmed
def home():
    """
    Get today's birthdays for the current user
    Returns: List of birthdays that match today's date
    """
    db = get_db()
    user_id = current_user.id
    birthdays = Birthdays.query.filter(
        func.strftime('%d-%m',Birthdays.birthdates)==func.strftime('%d-%m', func.now()),
        Birthdays.user_id==user_id
    ).all()

    for friend in birthdays:
        friend.age = calculate_age(friend.birthdates)
    
    return jsonify([{
        "id": friend.id,
        "name": friend.name,
        "email": friend.email,
        "phone": friend.phone,
        "birthdate": friend.birthdates,
        "age": friend.age
    } for friend in birthdays])

@main.route("/api/birthdays")
@login_required
@password_set
def birthdays():
    db = get_db()
    birthdays = Birthdays.query.filter_by(user_id=current_user.id).all()

    for friend in birthdays:
        friend.age = calculate_age(friend.birthdates)
    
    return jsonify([{
        "id": friend.id,
        "name": friend.name,
        "email": friend.email,
        "phone": friend.phone,
        "birthdate": friend.birthdates,
        "age": friend.age
    } for friend in birthdays])

@main.route("/api/add_birthday", methods=["POST"])
@login_required
@password_set
@email_confirmed
def add_birthday():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
        
    db = get_db()
    data = request.get_json()
    
    try:
        email = data.get("email")
        phone = data.get("phone")
        birthdate_str = data.get("birthdate")
        name = data.get("name")

        # Validate date format
        try:
            datetime.strptime(birthdate_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format! Use YYYY-MM-DD"}), 400

        birthdate = date_convert(birthdate_str)
        age = calculate_age(birthdate)

        if not all([name, birthdate, phone, email]):
            return jsonify({"error": "All fields are required!"}), 400
        
        birthday = Birthdays(
            user_id=current_user.id,
            name=name,
            birthdates=birthdate,
            phone=phone,
            email=email,
            age=age
        )
        db.add(birthday)
        db.commit()

        log(f"added_{name}")
        return jsonify({
            "message": f"{name} added successfully!",
            "success": True
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e), "success": False}), 400

@main.route("/api/delete_birthday/<int:id>", methods=["DELETE"])
@login_required
@password_set
def delete_friend(id):
    db = get_db()
    friend = Birthdays.query.filter_by(id=id, user_id=current_user.id).first()
    if not friend:
        return jsonify({"error": "Birthday not found!"}), 404
    name = friend.name
    try:
        db.delete(friend)
        db.commit()
        log(f"deleted_{name}")
        return jsonify({"message": f"{name} deleted successfully!"}), 200
    except:
        db.rollback()
        return jsonify({"error": "An error occurred while deleting birthday!"}), 500

@main.route("/api/edit_birthday/<int:id>", methods=["POST"])
@login_required
@password_set
@email_confirmed
def edit_birthday(id):
    db = get_db()
    friend = Birthdays.query.filter_by(id=id, user_id=current_user.id).first()

    if not friend:
        return jsonify({"error": "Birthday not found!"}), 404
    
    data = request.get_json()
    friend.email = data.get("email") or friend.email
    friend.phone = data.get("phone") or friend.phone
    friend.birthdates = date_convert(data.get("birthdate")) or friend.birthdates
    friend.name = data.get("name") or friend.name

    db.commit()

    log(f"edited_{friend.name}")
    return jsonify({"message": "Birthday updated successfully!"}), 200

@main.route("/api/update_profile/<int:id>", methods=["POST"])
@login_required
@password_set
@email_confirmed
def update_profile(id):
    db = get_db()
    user = Users.query.get_or_404(id)
    data = request.get_json()
    current_user.name = data.get("name") or current_user.name
    current_user.username = data.get("username") or current_user.username
    current_user.email = data.get("email") or current_user.email
    current_user.phone = data.get("phone") or current_user.phone
    current_user.dob = data.get("dob") or current_user.dob
    password = data.get("password")

    if not password or not check_password_hash(current_user.hash, password):
        return jsonify({"error": "Invalid password!"}), 400
    
    db.commit()
    log("profile_update")
    return jsonify({"message": "Profile updated successfully!"}), 200

@main.route("/api/logout")
@login_required
def logout():
    db = get_db()
    log("log out")
    logout_user()
    return jsonify({"message": "Logged out successfully!"}), 200

@main.route("/api/password_reset", methods=["POST"])
@login_required
@password_set
@email_confirmed
def password_reset():
    db = get_db()
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    confirmation = data.get("confirmation")
    hash = generate_password_hash(new_password, method='pbkdf2:sha256:600000', salt_length=16)
    
    if not old_password:
        return jsonify({"error": "Enter current password!"}), 400
    
    if not new_password or new_password != confirmation:
        return jsonify({"error": "Password mismatch!"}), 400
    
    current_user.hash = hash
    db.commit()
    
    log("pword_reset")
    return jsonify({"message": "Password changed successfully!"}), 200

@main.route("/api/search", methods=["POST"])
@login_required
@password_set
@email_confirmed
def search():
    db = get_db()
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Enter valid name!"}), 400
    else:
        searched_name = f"%{name}%"
        birthdays = Birthdays.query.filter(Birthdays.name.ilike(searched_name)).all()
        if not birthdays:
            return jsonify({"error": f"No friend with name {name}!"}), 404

        for friend in birthdays:
            birthdate = friend.birthdates
            friend.age = calculate_age(birthdate)

    return jsonify([{
        "id": friend.id,
        "name": friend.name,
        "email": friend.email,
        "phone": friend.phone,
        "birthdate": friend.birthdates,
        "age": friend.age
    } for friend in birthdays])

@main.route("/api/profile")
@login_required
@password_set
def profile():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "dob": current_user.dob
    })

@main.route("/api/delete_account", methods=["POST"])
@login_required
@password_set
def delete_account():
    db = get_db()
    data = request.get_json()
    password = data.get("password")
    
    if not password or not check_password_hash(current_user.hash, password):
        return jsonify({"error": "Invalid password!"}), 400
    
    friends = Birthdays.query.filter_by(user_id=current_user.id).all()
    
    for friend in friends:
        db.delete(friend)
    
    db.delete(current_user)
    db.commit()
    
    log('account_deleted')
    logout_user()
    return jsonify({"message": "Account deleted successfully!"}), 200


