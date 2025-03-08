from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty
from kivymd.uix.pickers import MDDatePicker
from mobile.utils.api_client import APIClient
from datetime import datetime, date
import re


class RegisterScreen(Screen):
    # Define properties for form fields
    username_field = ObjectProperty(None)
    name_field = ObjectProperty(None)
    email_field = ObjectProperty(None)
    phone_field = ObjectProperty(None)
    dob_field = ObjectProperty(None)
    password_field = ObjectProperty(None)
    confirmation_field = ObjectProperty(None)
    error_label = ObjectProperty(None)
    loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client = APIClient()

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None
        
    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def show_date_picker(self):
        """Show MDDatePicker dialog"""
        date_dialog = MDDatePicker(
            year=self.dob_field.text and int(self.dob_field.text.split('-')[0]) or date.today().year,
            month=self.dob_field.text and int(self.dob_field.text.split('-')[1]) or date.today().month,
            day=self.dob_field.text and int(self.dob_field.text.split('-')[2]) or date.today().day
        )
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()
    
    def on_date_save(self, instance, value, date_range):
        """Called when date is selected"""
        if value:
            self.dob_field.text = value.strftime("%Y-%m-%d")
            self.dob_field.error = False
    
    def register(self):
        self.ids.register_spinner.active = True
        user_data = {
            "username": self.username_field.text.strip(),
            "name": self.name_field.text.strip(),
            "email": self.email_field.text.strip(),
            "phone": self.phone_field.text.strip(),
            "dob": self.dob_field.text.strip(),
            "password": self.password_field.text.strip(),
            "confirmation": self.confirmation_field.text.strip()
        }

        if not all(user_data.values()):
            self.error_label.text = "All fields are required"
            self.ids.register_spinner.active = False
            return

        if user_data["password"] != user_data["confirmation"]:
            self.error_label.text = "Passwords do not match"
            self.ids.register_spinner.active = False
            return

        success = self.api_client.register(user_data)
        self.ids.register_spinner.active = False
        if success:
            self.manager.current = 'otp_verification'
        else:
            self.error_label.text = "Registration failed"

    def go_to_login(self):
        self.manager.current = 'login'
