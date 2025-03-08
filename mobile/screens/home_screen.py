from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from kivymd.uix.list import ThreeLineListItem
from mobile.utils.api_client import APIClient

class HomeScreen(Screen):
    birthday_list = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client = APIClient()
    
    def on_enter(self):
        """Called when screen is entered - refresh birthday data"""
        self.load_birthdays()
    
    def load_birthdays(self):
        """Load today's birthdays from API"""
        self.ids.birthday_list.clear_widgets()
        birthdays = self.api_client.get_todays_birthdays()
        
        if not birthdays:
            self.ids.birthday_list.add_widget(
                ThreeLineListItem(
                    text="No birthdays today!",
                    secondary_text="Add some birthdays to get started",
                    tertiary_text="Use the Add New button below"
                )
            )
            return
            
        for birthday in birthdays:
            # Ensure birthday is a dictionary and has required keys
            if isinstance(birthday, dict) and all(key in birthday for key in ['name', 'age', 'email', 'phone']):
                self.ids.birthday_list.add_widget(
                    ThreeLineListItem(
                        text=f"{birthday.get('name', 'Unknown')} - Age {birthday.get('age', '?')}",
                        secondary_text=f"📧 {birthday.get('email', 'No email')}",
                        tertiary_text=f"📱 {birthday.get('phone', 'No phone')}"
                    )
                )
    
    def view_all_birthdays(self):
        """Navigate to all birthdays screen"""
        self.manager.current = 'birthdays'
    
    def add_birthday(self):
        """Navigate to add birthday screen"""
        self.manager.current = 'add_birthday'
    
    def go_to_profile(self):
        """Navigate to profile screen"""
        self.manager.current = 'profile'
    
    def logout(self):
        """Handle logout"""
        if self.api_client.logout():
            self.manager.current = 'login'
