from django.urls import path
<<<<<<< HEAD
# from .views import show_club_directory 
=======
from .views import show_club_directory, get_club_details, toggle_favorite_club
>>>>>>> 4f2a6beb9985f8a7cd0299fd03121f9eb9a4d8df

app_name = 'club_directories'

urlpatterns = [
<<<<<<< HEAD
    # path('', show_club_directory, name='show_club_directory'),
=======
    path('', show_club_directory, name='show_club_directory'),
    path('club/<uuid:club_id>/', get_club_details, name='get_club_details'),
    path('toggle-favorite/', toggle_favorite_club, name='toggle_favorite_club'),
>>>>>>> 4f2a6beb9985f8a7cd0299fd03121f9eb9a4d8df
]
