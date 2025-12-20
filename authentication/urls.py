from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('profile/', profile_json, name='profile_json'),
    path('profile/edit/', profile_edit, name='edit_profile'),  
]