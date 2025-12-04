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
    
    # Team Details
    path('team/<uuid:club_id>/', views.team_detail, name='team_detail'),
    
    # Voting
    path('vote/<str:category>/<str:season>/', views.vote, name='vote'),
    path('vote-results/<str:category>/<str:season>/', views.vote_results, name='vote_results'),
    
    # Club of the Season Voting
    path('vote-club/<uuid:club_id>/', views.vote_for_club, name='vote_for_club'),
    path('delete-vote/', views.delete_vote, name='delete_vote'),
    path('club-voting-results/', views.voting_results, name='voting_results'),
    
    # Club Comparison
    path('compare/', views.compare_clubs, name='compare_clubs'),
    
    # Style Guide
    path('style-guide/', views.style_guide, name='style_guide'),
]