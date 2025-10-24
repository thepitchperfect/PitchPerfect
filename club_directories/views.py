# club_directories/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import League, Club
import json

# show_club_directory function remains the same...
def show_club_directory(request):
    leagues = League.objects.prefetch_related('clubs').all().order_by('name')
    leagues_data = []
    for league in leagues:
        short_id_map = {
            "Premier League": "PREM", "La Liga": "LALI", "Bundesliga": "BUND",
            "Serie A": "SERI", "Ligue 1 McDonald's": "LIG1", "Primeira Liga": "PRIM"
        }
        leagues_data.append({
            'id': str(league.id), 'name': league.name,
            'short_id': short_id_map.get(league.name, league.name[:4].upper()),
            'region': league.region, 'logo_path': league.logo_path,
            'coords': {
                "Premier League": [53.4, -2.2], "La Liga": [40.4, -3.7], "Bundesliga": [51.5, 10.5],
                "Serie A": [41.9, 12.5], "Ligue 1 McDonald's": [48.85, 2.35], "Primeira Liga": [38.7, -9.1]
            }.get(league.name, [0, 0]),
            'clubs': [{
                'id': str(club.id), 'name': club.name, 'logo_url': club.logo_url,
                'desc': f"Founded in {club.founded_year or 'N/A'}. Plays in {league.name}."
            } for club in league.clubs.all()]
        })
    context = {'leagues_data': leagues_data,}
    return render(request, 'club_directories/directory.html', context)


# Updated get_club_details
def get_club_details(request, club_id):
    club = get_object_or_404(Club.objects.select_related('league'), pk=club_id)
    data = {
        'id': str(club.id),
        'name': club.name,
        'logo_url': club.logo_url,
        'founded_year': club.founded_year,
        # stadium and fifa_ranking removed
        'league_id': str(club.league.id), # Send league ID
        'league_name': club.league.name,
        'league_logo_path': club.league.logo_path, # Send league logo path
        'region': club.league.region,
        # Add description (can be enhanced later)
        'description': f"A football club founded in {club.founded_year or 'N/A'}, currently playing in {club.league.name}, based in {club.league.region}.",
        # Add placeholder for history
        'history_summary': f"{club.name} has a rich history in {club.league.name}..." # Placeholder
    }
    return JsonResponse(data)