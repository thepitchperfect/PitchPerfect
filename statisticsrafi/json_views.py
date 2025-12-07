from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
import json
from .models import (
    Club, Award, Vote, ClubRanking, TeamStatistics, ClubVote
)
from club_directories.models import League

User = get_user_model()

def team_stats_to_dict(stat):
    """Helper to convert TeamStatistics object to dictionary"""
    return {
        'club_name': stat.club.name,
        'club_id': str(stat.club.id),
        'logo_url': stat.club.logo_url,
        'season': stat.season,
        'matches_played': stat.matches_played,
        'wins': stat.wins,
        'draws': stat.draws,
        'losses': stat.losses,
        'win_percentage': stat.win_percentage,
        'scored_per_match': float(stat.scored_per_match or 0),
        'conceded_per_match': float(stat.conceded_per_match or 0),
        'avg_match_goals': float(stat.avg_match_goals or 0),
        'clean_sheets_percentage': float(stat.clean_sheets_percentage or 0),
        'failed_to_score_percentage': float(stat.failed_to_score_percentage or 0),
        'possession_avg': float(stat.possession_avg or 0),
        'shots_taken_per_match': float(stat.shots_taken_per_match or 0),
        'shots_conversion_rate': float(stat.shots_conversion_rate or 0),
        'fouls_committed_per_match': float(stat.fouls_committed_per_match or 0),
        'fouled_against_per_match': float(stat.fouled_against_per_match or 0),
        'penalties_won': stat.penalties_won,
        'penalties_conceded': stat.penalties_conceded,
        'goal_kicks_per_match': float(stat.goal_kicks_per_match or 0),
        'throw_ins_per_match': float(stat.throw_ins_per_match or 0),
        'free_kicks_per_match': float(stat.free_kicks_per_match or 0),
    }

@require_GET
def get_general_stats_json(request):
    """API for the main statistics dashboard"""
    season = request.GET.get('season', '2025/26')
    
    # Top 10 Goals
    top_goals = TeamStatistics.objects.filter(season=season).order_by('-scored_per_match')[:10]
    top_goals_data = [team_stats_to_dict(stat) for stat in top_goals]
    
    # Top 10 Possession
    top_possession = TeamStatistics.objects.filter(season=season).order_by('-possession_avg')[:10]
    top_possession_data = [team_stats_to_dict(stat) for stat in top_possession]
    
    # Top 10 Clean Sheets
    top_clean_sheets = TeamStatistics.objects.filter(season=season).order_by('-clean_sheets_percentage')[:10]
    top_clean_sheets_data = [team_stats_to_dict(stat) for stat in top_clean_sheets]
    
    # Top 10 Rankings
    rankings = ClubRanking.objects.order_by('rank')[:10]
    rankings_data = [{
        'club_name': r.club.name,
        'club_id': str(r.club.id),
        'logo_url': r.club.logo_url,
        'rank': r.rank,
        'points': float(r.points),
        'continent': r.continent,
        'ranking_date': r.ranking_date,
        'previous_rank': r.previous_rank
    } for r in rankings]

    return JsonResponse({
        'top_goals': top_goals_data,
        'top_possession': top_possession_data,
        'top_clean_sheets': top_clean_sheets_data,
        'rankings': rankings_data
    })

@require_GET
def get_specific_stat_json(request, category):
    """API for specific full lists"""
    season = request.GET.get('season', '2025/26')
    data = []
    
    if category == 'goals':
        stats = TeamStatistics.objects.filter(season=season).order_by('-scored_per_match')
        data = [team_stats_to_dict(s) for s in stats]
    elif category == 'possession':
        stats = TeamStatistics.objects.filter(season=season).order_by('-possession_avg')
        data = [team_stats_to_dict(s) for s in stats]
    elif category == 'clean_sheets':
        stats = TeamStatistics.objects.filter(season=season).order_by('-clean_sheets_percentage')
        data = [team_stats_to_dict(s) for s in stats]
    elif category == 'rankings':
        ranks = ClubRanking.objects.order_by('rank')
        data = [{
            'club_name': r.club.name,
            'club_id': str(r.club.id),
            'logo_url': r.club.logo_url,
            'rank': r.rank,
            'points': float(r.points),
            'continent': r.continent,
            'ranking_date': r.ranking_date,
            'previous_rank': r.previous_rank
        } for r in ranks]
    elif category == 'awards':
        clubs_with_awards = Club.objects.annotate(
            award_count=Count('awards')
        ).filter(award_count__gt=0).order_by('-award_count')
        
        data = []
        for club in clubs_with_awards:
            club_awards = Award.objects.filter(club=club).order_by('-date_awarded')
            awards_list = [{
                'title': a.title,
                'award_type': a.get_award_type_display(),
                'season': a.season,
                'date': a.date_awarded,
                'description': a.description
            } for a in club_awards]
            
            data.append({
                'club_name': club.name,
                'club_id': str(club.id),
                'logo_url': club.logo_url,
                'award_count': club.award_count,
                'awards': awards_list
            })
            
    return JsonResponse({'results': data, 'category': category, 'season': season})

@require_GET
def get_team_detail_json(request, club_id):
    """API for team details"""
    club = get_object_or_404(Club, id=club_id)
    team_stats = TeamStatistics.objects.filter(club=club).order_by('-season').first()
    
    # Get club rankings
    club_ranking = ClubRanking.objects.filter(club=club).order_by('-ranking_date').first()
    
    # Get club awards
    club_awards = Award.objects.filter(club=club).order_by('-date_awarded')
    
    # User vote status
    user_vote_status = {
        'has_voted': False,
        'voted_for_this_club': False
    }
    
    if request.user.is_authenticated:
        user_vote = ClubVote.objects.filter(user=request.user, season='2025/26').first()
        if user_vote:
            user_vote_status['has_voted'] = True
            user_vote_status['voted_for_this_club'] = (user_vote.club == club)

    response_data = {
        'club': {
            'name': club.name,
            'id': str(club.id),
            'logo_url': club.logo_url,
            'league': club.league.name if club.league else "N/A",
            'founded': club.founded_year
        },
        'stats': team_stats_to_dict(team_stats) if team_stats else None,
        'ranking': {
            'rank': club_ranking.rank,
            'points': float(club_ranking.points),
            'continent': club_ranking.continent
        } if club_ranking else None,
        'awards': [{
            'title': a.title,
            'season': a.season,
            'date': a.date_awarded
        } for a in club_awards],
        'user_vote': user_vote_status
    }
    
    return JsonResponse(response_data)

@csrf_exempt
@require_POST
def vote_club_json(request):
    """API to vote for a club"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=401)
    
    try:
        data = json.loads(request.body)
        club_id = data.get('club_id')
        season = data.get('season', '2025/26')
        
        club = get_object_or_404(Club, id=club_id)
        
        existing_vote = ClubVote.objects.filter(user=request.user, season=season).first()
        
        if existing_vote:
            if existing_vote.club == club:
                return JsonResponse({
                    'status': 'info',
                    'message': f'You have already voted for {club.name} for {season}.'
                })
            else:
                existing_vote.club = club
                existing_vote.save()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Vote changed to {club.name}.'
                })
        else:
            ClubVote.objects.create(user=request.user, club=club, season=season)
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully voted for {club.name}.'
            })
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_GET
def get_vote_results_json(request):
    """API for vote results"""
    season = request.GET.get('season', '2025/26')
    
    vote_counts = ClubVote.objects.filter(season=season).values(
        'club__name', 'club__logo_url'
    ).annotate(
        vote_count=Count('id')
    ).order_by('-vote_count')
    
    results = [{
        'club_name': v['club__name'],
        'logo_url': v['club__logo_url'],
        'vote_count': v['vote_count']
    } for v in vote_counts]
    
    total_votes = ClubVote.objects.filter(season=season).count()
    
    user_vote_club = None
    if request.user.is_authenticated:
        user_vote = ClubVote.objects.filter(user=request.user, season=season).first()
        if user_vote:
            user_vote_club = user_vote.club.name

    return JsonResponse({
        'results': results,
        'total_votes': total_votes,
        'user_vote': user_vote_club,
        'season': season
    })

@require_GET
def get_all_clubs_json(request):
    """API to get all clubs (for dropdowns)"""
    clubs = Club.objects.all().order_by('name')
    data = [{'id': str(c.id), 'name': c.name, 'logo_url': c.logo_url} for c in clubs]
    return JsonResponse({'clubs': data})
