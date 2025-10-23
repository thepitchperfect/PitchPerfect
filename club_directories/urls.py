from django.urls import path
from .views import show_club_directory 

app_name = 'club_directories'

urlpatterns = [
    path('', show_club_directory, name='show_club_directory'),
]

