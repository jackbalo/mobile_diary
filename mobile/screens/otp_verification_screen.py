from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from mobile.utils.api_client import APIClient

class OTPVerificationScreen(Screen):
    otp_input = ObjectProperty(None)
    error_label = ObjectProperty(None)
    countdown_label = ObjectProperty(None)
    resend_button = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client = APIClient()
    
    def verify_otp(self):
        otp = self.otp_input.text.strip()
        if not otp:
            self.error_label.text = "Please enter OTP"
            return
        
        success = self.api_client.verify_otp(otp)
        if success:
            self.manager.current = 'home'
        else:
            self.error_label.text = "Invalid or expired OTP"
    
    def resend_otp(self):
        success = self.api_client.request_new_otp()
        if success:
            self.error_label.text = "OTP resent successfully"
        else:
            self.error_label.text = "Failed to resend OTP"
