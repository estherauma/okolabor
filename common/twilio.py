from twilio.rest import Client
from decouple import config

class OTPVerification:
    def __init__(self):
        self.account_sid = config('TWILIO_ACCOUNT_SID')
        self.auth_token = config('TWILIO_AUTH_TOKEN')
        self.verify_sid = config('TWILIO_VERIFY_SID')
        self.verified_number = config('TWILIO_VERIFIED_PHONE_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)

    def send_otp(self):
        verification = self.client.verify.v2.services(self.verify_sid) \
            .verifications \
            .create(to=self.verified_number, channel="sms")
        print("OTP sent to:", self.verified_number)
        return verification.status

    def check_otp(self, otp_code):
        verification_check = self.client.verify.v2.services(self.verify_sid) \
            .verification_checks \
            .create(to=self.verified_number, code=otp_code)
        return verification_check.status
