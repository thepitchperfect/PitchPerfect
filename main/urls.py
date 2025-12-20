from django.urls import path
from .views import show_main, register_user, login_user, logout_user, profile, profile_edit, show_json

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('json/', show_json, name='show_json'),
]