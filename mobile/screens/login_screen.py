from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from mobile.utils.api_client import APIClient

class LoginScreen(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    error_label = ObjectProperty(None)
    login_spinner = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client = APIClient()

    def login(self):
        self.login_spinner.active = True
        username = self.username.text.strip()
        password = self.password.text.strip()

        if not username or not password:
            self.error_label.text = "Must provide Username and Password"
            self.login_spinner.active = False
            return

        success, _ = self.api_client.login(username, password)
        self.login_spinner.active = False
        
        if success:
            self.error_label.text = ""  # Clear any previous errors
            self.manager.current = 'home'
        else:
            self.error_label.text = "Invalid username and/or password"

    def go_to_register(self):
        self.manager.current = 'register'
