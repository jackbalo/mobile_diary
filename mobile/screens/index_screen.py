from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

class IndexScreen(Screen):
    def go_to_login(self):
        self.manager.current = 'login'
        
    def go_to_register(self):
        self.manager.current = 'register'
        
    def show_terms(self):
        # TODO: Implement terms and services dialog/screen
        pass
