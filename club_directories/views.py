from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404 
from .models import League, Club, ClubDetails, LeaguePick
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import json
from django.views.decorators.csrf import csrf_exempt

def show_club_directory(request):
    leagues = League.objects.prefetch_related('clubs').all().order_by('name')
    
    # Get League Picks
    league_picks = {}
    if request.user.is_authenticated:
        picks = LeaguePick.objects.filter(user=request.user).select_related('club')
        for pick in picks:
            league_picks[str(pick.league_id)] = {
                'clubId': str(pick.club_id),
                'clubName': pick.club.name,
                'logoUrl': pick.club.logo_url
            }

    # Coordinates mapping for known leagues
    COORD_MAP = {
        "Premier League": [52.3555, -1.1743],       # UK
        "La Liga": [40.4637, -3.7492],              # Spain
        "Bundesliga": [51.1657, 10.4515],           # Germany
        "Serie A": [41.8719, 12.5674],              # Italy
        "Ligue 1 McDonald's": [46.603354, 1.888334], # France
        "Primeira Liga": [39.3999, -8.2245]         # Portugal
    }

    leagues_data = []
    for league in leagues:
        short_id_map = {
            "Premier League": "PREM", "La Liga": "LALI", "Bundesliga": "BUND",
            "Serie A": "SERI", "Ligue 1 McDonald's": "LIG1", "Primeira Liga": "PRIM"
        }
        
        # Get coords from map, or default to Paris if name doesn't match
        league_coords = COORD_MAP.get(league.name, [48.8566, 2.3522])

        leagues_data.append({
            'id': str(league.id), 
            'name': league.name,
            'short_id': short_id_map.get(league.name, league.name[:3].upper()),
            'logo_path': league.logo_path,
            'coords': league_coords, 
            'clubs': [{
                'id': str(c.id), 'name': c.name, 
                'logo_url': c.logo_url,
                'desc': c.details.description[:100] + '...' if hasattr(c, 'details') and c.details.description else "No description available."
            } for c in league.clubs.all()]
        })

    return render(request, 'club_directories/directory.html', {
        'leagues_data': leagues_data,
        'league_picks_data': league_picks
    })

def get_club_details(request, club_id):
    try:
        club = Club.objects.select_related('league').get(pk=club_id)
        
        try:
            details = club.details
            description = details.description
            history = details.history_summary
            stadium = details.stadium_name
            capacity = details.stadium_capacity
            manager = details.manager_name
        except ClubDetails.DoesNotExist:
            description = ""
            history = ""
            stadium = ""
            capacity = None
            manager = ""

        # Generate URL for statistics module
        try:
            stats_url = reverse('statisticsrafi:team_detail', args=[club.id])
        except Exception:
            stats_url = "#"

        data = {
            'id': str(club.id),
            'name': club.name,
            'league_name': club.league.name,
            'league_id': str(club.league.id),
            'league_logo_path': club.league.logo_path,
            'logo_url': club.logo_url,
            'founded_year': club.founded_year,
            'description': description,
            'history_summary': history,
            'stadium_name': stadium,
            'stadium_capacity': capacity,
            'stadium_capacity_str': f"{capacity:,}" if capacity else "N/A",
            'manager_name': manager,
            'stats_url': stats_url
        }
        
        if request.user.is_authenticated:
            is_pick = LeaguePick.objects.filter(user=request.user, league=club.league, club=club).exists()
            data['is_league_pick'] = is_pick

        return JsonResponse(data)
    except Club.DoesNotExist:
        raise Http404("Club not found")

@csrf_exempt
@login_required
def set_league_pick(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
    
    # --- DEBUG PRINTS (Check your terminal!) ---
    print(f"DEBUG: Content Type: {request.content_type}")
    print(f"DEBUG: Body: {request.body}")
    print(f"DEBUG: POST Data: {request.POST}")
    
    club_id = None
    league_id = None

    # 1. Try JSON Parsing
    try:
        data = json.loads(request.body)
        club_id = data.get('club_id')
        league_id = data.get('league_id')
        print(f"DEBUG: Parsed JSON - Club: {club_id}, League: {league_id}")
    except (json.JSONDecodeError, AttributeError):
        pass

    # 2. Fallback to POST Form Data (if JSON failed or wasn't sent)
    if not club_id:
        club_id = request.POST.get('club_id')
        league_id = request.POST.get('league_id')
        print(f"DEBUG: Parsed POST - Club: {club_id}, League: {league_id}")

    if not league_id:
         return JsonResponse({'status': 'error', 'message': 'League ID is required.'}, status=400)
    
    if not club_id:
         return JsonResponse({'status': 'error', 'message': 'Club ID is required.'}, status=400)

    try:
        if club_id == 'NONE':
            league = get_object_or_404(League, pk=league_id) 
            LeaguePick.objects.filter(user=request.user, league=league).delete()
            return JsonResponse({'status': 'cleared', 'league_id': league_id})

        club = get_object_or_404(Club, pk=club_id) 
        league = club.league

        pick, created = LeaguePick.objects.update_or_create(
            user=request.user, 
            league=league,
            defaults={'club': club}
        )

        club_data = {
            'clubId': str(club.id),
            'clubName': club.name,
            'logoUrl': club.logo_url
        }
        
        return JsonResponse({
            'status': 'set', 
            'league_id': str(league.id),
            'club_data': club_data
        })
            
    except Http404:
        message = 'Object not found.'
        # simplified check
        return JsonResponse({'status': 'error', 'message': message}, status=404)
    except Club.DoesNotExist: 
        return JsonResponse({'status': 'error', 'message': 'Club not found.'}, status=404)
    except League.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'League not found.'}, status=404)
    except Exception as e:
        print(f"DEBUG: Exception: {str(e)}") # Print exception to terminal
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def show_json_directory(request):
    leagues = League.objects.prefetch_related('clubs').all().order_by('name')
    
    # Coordinates mapping (Same as in show_club_directory)
    COORD_MAP = {
        "Premier League": [52.3555, -1.1743],       # UK
        "La Liga": [40.4637, -3.7492],              # Spain
        "Bundesliga": [51.1657, 10.4515],           # Germany
        "Serie A": [41.8719, 12.5674],              # Italy
        "Ligue 1 McDonald's": [46.603354, 1.888334], # France
        "Primeira Liga": [39.3999, -8.2245]         # Portugal
    }

    data = []
    for league in leagues:
        clubs = []
        for club in league.clubs.all():
            clubs.append({
                'id': str(club.id),
                'name': club.name,
                'logo_url': club.logo_url,
                'founded_year': club.founded_year,
                'desc': club.details.description[:100] + '...' if hasattr(club, 'details') and club.details.description else "No description available."
            })
        
        # Get coords from map, or default to Paris
        league_coords = COORD_MAP.get(league.name, [48.8566, 2.3522])
        
        data.append({
            'id': str(league.id),
            'name': league.name,
            'region': league.region,
            'coords': league_coords,  # Added coords here
            'clubs': clubs
        })

    picks_data = {}
    if request.user.is_authenticated:
        picks = LeaguePick.objects.filter(user=request.user).select_related('club')
        for pick in picks:
            picks_data[str(pick.league_id)] = {
                'clubId': str(pick.club_id),
                'clubName': pick.club.name,
                'logoUrl': pick.club.logo_url
            }

    return JsonResponse({'leagues': data, 'picks': picks_data})