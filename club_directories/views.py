from django.shortcuts import render
from .models import League, FavoriteClub
import json 

def show_club_directory(request):
    
    league_coords = {
        'Premier League': [53.4, -2.2],
        'La Liga': [40.4, -3.7],
        'Bundesliga': [52.5, 13.4],
        'Serie A': [41.9, 12.5],
        'Ligue 1 McDonald\'s': [48.85, 2.35],
        'Primeira Liga': [38.7, -9.1] 
    }

    leagues = League.objects.all().prefetch_related('clubs').order_by('name')

    league_data_list = []
    favorite_club_ids = [] 

    if request.user.is_authenticated:
        favorite_club_ids = [
            str(uuid) for uuid in 
            FavoriteClub.objects.filter(user=request.user).values_list('club_id', flat=True)
        ]

    for league in leagues:
        clubs_list = []
        for club in league.clubs.all():
            clubs_list.append({
                'id': str(club.id), 
                'name': club.name,
                'logo_url': club.logo_url,
                'founded_year': club.founded_year,
                'desc': f"Founded in {club.founded_year or 'N/A'}. Plays in {league.name}." 
            })
        
        league_data_list.append({
            'id': str(league.id), 
            'short_id': league.name.replace(" ", "")[:4].upper(), 
            'name': league.name,
            'region': league.region,
            'logo_path': league.logo_path, 
            'coords': league_coords.get(league.name, [45, 0]), 
            'clubs': clubs_list
        })

    context = {
        'leagues_data': league_data_list,
        'favorite_club_ids_list': favorite_club_ids 
    }
    
    return render(request, 'club_directories/directory.html', context)

