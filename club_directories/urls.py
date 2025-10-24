from django.urls import path
from .views import show_club_directory, get_club_details

app_name = 'club_directories'

urlpatterns = [
    path('', show_club_directory, name='show_club_directory'),
    path('club/<uuid:club_id>/', get_club_details, name='get_club_details'),
]