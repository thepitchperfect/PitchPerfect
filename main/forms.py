from django.contrib.auth.forms import UserCreationForm
from django.utils.html import strip_tags
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'full_name')

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return strip_tags(username)

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name")
        return strip_tags(full_name)

