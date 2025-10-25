from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import League, Club, FavoriteClub, ClubDetails
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json

def show_club_directory(request):
    leagues = League.objects.prefetch_related('clubs').all().order_by('name')
    
    favorite_club_ids = set()
    if request.user.is_authenticated:
        favorite_club_ids = set(
            FavoriteClub.objects.filter(user=request.user).values_list('club_id', flat=True)
        )

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
                'id': club.id,
                'name': club.name, 
                'logo_url': club.logo_url,
                'desc': f"Founded in {club.founded_year or 'N/A'}. Plays in {league.name}.",
                'is_favorite': club.id in favorite_club_ids
            } for club in league.clubs.all()]
        })
    
    context = {
        'leagues_data': leagues_data,
    }
    return render(request, 'club_directories/directory.html', context)

def get_club_details(request, club_id):
    club = get_object_or_404(Club.objects.select_related('league'), pk=club_id)
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteClub.objects.filter(user=request.user, club=club).exists()
    try:
        details = club.details 
        description = details.description
        history_summary = details.history_summary
        stadium_name = details.stadium_name
        stadium_capacity = details.stadium_capacity
        manager_name = details.manager_name
    except ClubDetails.DoesNotExist:
        description = f"A football club founded in {club.founded_year or 'N/A'}, currently playing in {club.league.name}, based in {club.league.region}."
        history_summary = f"{club.name} has a rich history in {club.league.name}..." # Placeholder
        stadium_name = "N/A"
        stadium_capacity = None
        manager_name = "N/A"

    data = {
        'id': str(club.id),
        'name': club.name,
        'logo_url': club.logo_url,
        'founded_year': club.founded_year,
        'league_id': str(club.league.id), 
        'league_name': club.league.name,
        'league_logo_path': club.league.logo_path,
        'region': club.league.region,
        'is_favorite': is_favorite,
        'description': description,
        'history_summary': history_summary,
        'stadium_name': stadium_name,
        'stadium_capacity_str': f"{stadium_capacity:,}" if stadium_capacity else "N/A", 
        'manager_name': manager_name,
    }
    return JsonResponse(data)

@login_required
@require_POST
def toggle_favorite_club(request):
    try:
        club_id = request.POST.get('club_id')
        if not club_id:
            return JsonResponse({'status': 'error', 'message': 'Club ID is required.'}, status=400)
            
        club = get_object_or_404(Club, pk=club_id)
        
        favorite, created = FavoriteClub.objects.get_or_create(user=request.user, club=club)
        
        if created:
            return JsonResponse({'status': 'added', 'is_favorite': True})
        else:
            favorite.delete()
            return JsonResponse({'status': 'removed', 'is_favorite': False})
            
    except Club.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Club not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
