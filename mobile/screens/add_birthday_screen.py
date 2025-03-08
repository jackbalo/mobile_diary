from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty
from mobile.utils.api_client import APIClient
from datetime import datetime, date

class AddBirthdayScreen(Screen):
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

    def save_birthday(self):
        # Show spinner
        self.ids.addbirthday_spinner.active = True
        
        # Get and validate input data
        birthday_data = {
            "name": self.ids.name.text.strip(),
            "email": self.ids.email.text.strip(),
            "phone": self.ids.phone.text.strip(),
            "birthdate": self.ids.dob.text.strip()
        }

        # Validate inputs
        if not all(birthday_data.values()):
            self.ids.error_label.text = "All fields are required!"
            self.ids.addbirthday_spinner.active = False
            return

        # Validate date format
        try:
            datetime.strptime(birthday_data["birthdate"], "%Y-%m-%d")
        except ValueError:
            self.ids.error_label.text = "Invalid date format! Use YYYY-MM-DD"
            self.ids.addbirthday_spinner.active = False
            return

        # Send to API and handle response
        success = self.api_client.add_birthday(birthday_data)
        self.ids.addbirthday_spinner.active = False
        
        if success:
            self.clear_fields()
            self.manager.current = 'home'
        else:
            self.ids.error_label.text = "Failed to add birthday. Please try again."
          

    def clear_fields(self):
        """Clear all input fields"""
        self.ids.name.text = ""
        self.ids.email.text = ""
        self.ids.phone.text = ""
        self.ids.date.text = ""
        self.ids.error_label.text = ""

    def cancel(self):
        """Cancel and return to home screen"""
        self.clear_fields()
        self.manager.current = 'home'
