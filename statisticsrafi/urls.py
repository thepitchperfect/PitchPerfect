from django.urls import path
from . import views

app_name = 'statisticsrafi'

urlpatterns = [
    # Home
    path('', views.statistics_home, name='home'),
    
    # Statistics Lists
    path('top-scorers/', views.top_scorers, name='top_scorers'),
    path('top-scorers/<str:season>/', views.top_scorers, name='top_scorers_season'),
    path('top-assisters/', views.top_assisters, name='top_assisters'),
    path('top-assisters/<str:season>/', views.top_assisters, name='top_assisters_season'),
    path('clean-sheets/', views.most_clean_sheets, name='clean_sheets'),
    path('clean-sheets/<str:season>/', views.most_clean_sheets, name='clean_sheets_season'),
    path('most-awards/', views.most_awards, name='most_awards'),
    path('club-rankings/', views.club_rankings, name='club_rankings'),
    
    # Player Details
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    
    # Team Details
    path('team/<uuid:club_id>/', views.team_detail, name='team_detail'),
    
    # Watchlist (CRUD)
    path('watchlist/', views.my_watchlist, name='my_watchlist'),
    path('watchlist/add/<int:player_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:watchlist_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/update/<int:watchlist_id>/', views.update_watchlist_notes, name='update_watchlist_notes'),
    
    # Voting
    path('vote/<str:category>/<str:season>/', views.vote, name='vote'),
    path('vote-results/<str:category>/<str:season>/', views.vote_results, name='vote_results'),
    
    # Player Comparison
    path('compare/', views.compare_players, name='compare_players'),
    path('my-comparisons/', views.my_comparisons, name='my_comparisons'),
    
    # Style Guide
    path('style-guide/', views.style_guide, name='style_guide'),
]