from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class CustomUserBackend(ModelBackend):
    """
    A custom authentication backend for the CustomUser model.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Overrides the authenticate method to use CustomUser.
        """
        try:
            # Try to find a user matching the given username
            user = CustomUser.objects.get(username=username)
            
            # Check the password
            if user.check_password(password):
                return user  # Authentication successful
        except CustomUser.DoesNotExist:
            # No user found with that username
            return None
        
        return None  # Password was incorrect

    def get_user(self, user_id):
        """
        Overrides the get_user method to retrieve a CustomUser instance.
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
