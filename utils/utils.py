from django.core.mail import EmailMessage
import threading
import pytz
import datetime


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()



# def get_user_timezone(request):
#     """Get timezone from user preferences or default to UTC"""
#     try:
#         user_timezone = request.user.profile.timezone
#         return pytz.timezone(user_timezone)
#     except (AttributeError, pytz.exceptions.UnknownTimeZoneError):
#         return pytz.UTC

# def convert_to_local_time(dt, timezone_str):
#     """Convert datetime to specified timezone"""
#     if not dt.tzinfo:
#         dt = pytz.UTC.localize(dt)
#     try:
#         local_tz = pytz.timezone(timezone_str)
#         return dt.astimezone(local_tz)
#     except pytz.exceptions.UnknownTimeZoneError:
#         return dt.astimezone(pytz.UTC)