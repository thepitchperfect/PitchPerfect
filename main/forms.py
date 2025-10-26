from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, CharField, TextInput, URLInput
from django.utils.html import strip_tags
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'full_name')

    def clean_username(self):
        username = self.cleaned_data["username"]
        return strip_tags(username)

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"]
        return strip_tags(full_name)


class CustomUserChangeForm(ModelForm):
    username = CharField(
        disabled=True, 
        required=False,
        widget=TextInput(attrs={'class': 'w-full px-3 py-2 font-lato text-sm md:text-lg rounded-md bg-gray-100 text-gray-500 cursor-not-allowed shadow-inner'})
    )

    class Meta:
        model = CustomUser
        fields = ("profpict", "username", "full_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.username

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"]
        return strip_tags(full_name)

