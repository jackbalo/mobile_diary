from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from mobile.utils.api_client import APIClient

class ProfileScreen(Screen):
    name_field = ObjectProperty(None)
    username_field = ObjectProperty(None)
    email_field = ObjectProperty(None)
    phone_field = ObjectProperty(None)
    dob_field = ObjectProperty(None)
    error_label = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client = APIClient()
    
    def on_enter(self):
        """Load user profile data when screen is entered"""
        user_data = self.api_client.get_profile()
        if user_data:
            self.name_field.text = user_data.get('name', '')
            self.username_field.text = user_data.get('username', '')
            self.email_field.text = user_data.get('email', '')
            self.phone_field.text = user_data.get('phone', '')
            self.dob_field.text = user_data.get('dob', '')
    
    def update_profile(self):
        """Update user profile"""
        success = self.api_client.update_profile({
            'id': self.api_client.get_profile().get('id'),
            'name': self.name_field.text,
            'username': self.username_field.text,
            'email': self.email_field.text,
            'phone': self.phone_field.text,
            'dob': self.dob_field.text
        })
        if success:
            self.error_label.text = "Profile updated successfully"
        else:
            self.error_label.text = "Failed to update profile"
