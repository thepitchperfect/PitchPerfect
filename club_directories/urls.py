from django.urls import path
from .views import show_club_directory, get_club_details, set_league_pick ,show_json_directory

app_name = 'club_directories'

urlpatterns = [
    path('', show_club_directory, name='show_club_directory'),
    path('club/<uuid:club_id>/', get_club_details, name='get_club_details'),
    path('set-league-pick/', set_league_pick, name='set_league_pick'),
    path('json/', show_json_directory, name='show_json_directory'),
]