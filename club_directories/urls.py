from django.urls import path
from .views import show_club_directory, get_club_details, toggle_favorite_club

app_name = 'club_directories'

urlpatterns = [
    path('', show_club_directory, name='show_club_directory'),
    path('club/<uuid:club_id>/', get_club_details, name='get_club_details'),
    path('toggle-favorite/', toggle_favorite_club, name='toggle_favorite_club'),
]
