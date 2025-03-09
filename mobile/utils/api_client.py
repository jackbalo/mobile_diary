import requests
from urllib.parse import urljoin
from shared.models import Users, Birthdays
from shared.database import db_session

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.token = None
        self.session_db = db_session  # Use the scoped session

    def login(self, username, password):
        url = urljoin(self.base_url, "/api/login")
        try:
            response = self.session.post(url, json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                # Store any session cookies automatically
                return True, data.get('email_confirmed', False)
            return False, False
        except requests.RequestException:
            return False, False

    def register(self, user_data):
        url = urljoin(self.base_url, "/api/register")
        try:
            response = self.session.post(url, json=user_data)
            return response.status_code == 201
        except requests.RequestException:
            return False

    def verify_otp(self, otp):
        url = urljoin(self.base_url, "/api/otp_verification")
        try:
            response = self.session.post(url, json={"otp": otp})
            return response.status_code == 200
        except requests.RequestException:
            return False

    def request_new_otp(self):
        url = urljoin(self.base_url, "/api/otp_verification")
        try:
            response = self.session.post(url, json={"resend_otp": "1"})
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_profile(self):
        url = urljoin(self.base_url, "/api/profile")
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                user_data = response.json()
                return user_data.get('confirmed', False)
            return False
        except requests.RequestException:
            return False

    def get_birthdays(self):
        url = urljoin(self.base_url, "/api/birthdays")
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException:
            return []

    def add_birthday(self, birthday_data):
        url = urljoin(self.base_url, "/api/add_birthday")
        try:
            response = self.session.post(url, json=birthday_data)
            if response.status_code == 201:
                return response.json()
        except requests.RequestException:
            return False

    def update_profile(self, profile_data):
        url = urljoin(self.base_url, f"/api/update_profile/{profile_data['id']}")
        try:
            response = self.session.post(url, json=profile_data)
            return response.status_code == 200
        except requests.RequestException:
            return {"error": str(e), "success": False}


    def search_birthdays(self, name):
        url = urljoin(self.base_url, "/api/search")
        try:
            response = self.session.post(url, json={"name": name})
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException:
            return []

    def logout(self):
        url = urljoin(self.base_url, "/api/logout")
        try:
            response = self.session.post(url)
            self.token = None
            return response.status_code == 200
        except requests.RequestException:
            return False

    def delete_account(self, password):
        url = urljoin(self.base_url, "/api/delete_account")
        try:
            response = self.session.post(url, json={"password": password})
            return response.status_code == 200
        except requests.RequestException:
            return False

    def reset_password(self, old_password, new_password, confirmation):
        url = urljoin(self.base_url, "/api/password_reset")
        try:
            response = self.session.post(url, json={
                "old_password": old_password,
                "new_password": new_password,
                "confirmation": confirmation
            })
            return response.status_code == 200
        except requests.RequestException:
            return False

    def add_password(self, password, confirmation):
        url = urljoin(self.base_url, "/api/add_password")
        try:
            response = self.session.post(url, json={
                "password": password,
                "confirmation": confirmation
            })
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_todays_birthdays(self):
        url = urljoin(self.base_url, "/api/home")
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException:
            return []
