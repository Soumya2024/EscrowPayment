# from django.contrib.auth.backends import ModelBackend
# from .models import RegisterModel

# class ActiveUserBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             user = RegisterModel.objects.get(email=username)
#             if user.password == password: 
#                 if user.is_active:
#                     return user
#                 else:
#                     return {None} 
#         except RegisterModel.DoesNotExist:
#             return None 
#         return None



# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class ActiveUserBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         # Try to get the user
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return None

#         # Check if the password is correct
#         if user.check_password(password) and self.user_can_authenticate(user):
#             return user
#         return None

#     def user_can_authenticate(self, user):
#         """Check if the user is active."""
#         return user.is_active  # Only allow active users to authenticate
