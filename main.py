import os
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.lang import Builder
from kivy.core.window import Window
from mobile.screens.index_screen import IndexScreen
from mobile.screens.login_screen import LoginScreen
from mobile.screens.register_screen import RegisterScreen
from mobile.screens.home_screen import HomeScreen
from mobile.screens.profile_screen import ProfileScreen
from mobile.screens.otp_verification_screen import OTPVerificationScreen
from mobile.screens.add_birthday_screen import AddBirthdayScreen

class DiaryMobileApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set initial window size for testing
        Window.size = (400, 600)
        
        # Remove database initialization from mobile app
        # Base.metadata.drop_all(engine)  # Only in development
        # Base.metadata.create_all(engine)

    def build(self):
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set theme before loading KV files
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.theme_style = "Light"
        
        # Load all kv files with absolute paths
        Builder.load_file(os.path.join(current_dir, 'mobile', 'kv', 'index.kv'))
        Builder.load_file(os.path.join(current_dir, 'mobile', 'kv', 'login.kv'))
        Builder.load_file(os.path.join(current_dir, 'mobile', 'kv', 'register.kv'))
        Builder.load_file(os.path.join(current_dir, 'mobile', 'kv', 'home.kv'))
        Builder.load_file(os.path.join(current_dir, 'mobile', 'kv', 'profile.kv'))
        Builder.load_file(os.path.join(current_dir, 'mobile', 'kv', 'otp_verification.kv'))
        Builder.load_file(os.path.join(current_dir, 'mobile', 'kv', 'add_birthday.kv'))

        # Create screen manager
        sm = ScreenManager(transition=NoTransition())
        
        # Add screens
        sm.add_widget(IndexScreen(name='index'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(OTPVerificationScreen(name='otp_verification'))
        sm.add_widget(AddBirthdayScreen(name='add_birthday'))

        # Set initial screen to index
        sm.current = 'index'

        return sm

if __name__ == '__main__':
    DiaryMobileApp().run()
