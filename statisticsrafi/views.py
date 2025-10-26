from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.contrib import messages
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from .models import (
    Player, Club, PlayerStatistics, Award, 
    UserWatchlist, Vote, PlayerComparison, ClubRanking, TeamStatistics, ClubVote
)

# READ - List Views
def statistics_home(request):
    """Main statistics dashboard"""
    context = {
        'top_goals': TeamStatistics.objects.filter(season='2025/26').order_by('-scored_per_match')[:10],
        'top_possession': TeamStatistics.objects.filter(season='2025/26').order_by('-possession_avg')[:10],
        'top_clean_sheets': TeamStatistics.objects.filter(season='2025/26').order_by('-clean_sheets_percentage')[:10],
        'club_rankings': ClubRanking.objects.order_by('rank')[:20],
    }
    return render(request, 'statisticsrafi/home.html', context)

def top_scorers(request, season='2025/26'):
    """Top goals based on club stats"""
    top_goals = TeamStatistics.objects.filter(season=season).order_by('-scored_per_match')
    return render(request, 'statisticsrafi/top_scorers.html', {'scorers': top_goals, 'season': season})

def top_assisters(request, season='2025/26'):
    """Top possession average based on club stats"""
    top_possession = TeamStatistics.objects.filter(season=season).order_by('-possession_avg')
    return render(request, 'statisticsrafi/top_assisters.html', {'assisters': top_possession, 'season': season})

def most_clean_sheets(request, season='2025/26'):
    """Top clean sheets based on club stats"""
    top_clean_sheets = TeamStatistics.objects.filter(season=season).order_by('-clean_sheets_percentage')
    return render(request, 'statisticsrafi/clean_sheets.html', {'clean_sheets': top_clean_sheets, 'season': season})

def most_awards(request):
    """Players and clubs with most awards"""
    from club_directories.models import Club
    
    players_with_awards = Player.objects.annotate(
        award_count=Count('awards')
    ).filter(award_count__gt=0).order_by('-award_count')
    
    clubs_with_awards = Club.objects.annotate(
        award_count=Count('awards')
    ).filter(award_count__gt=0).order_by('-award_count')
    
    # Get all club awards ordered by date
    club_awards = Award.objects.filter(club__isnull=False).select_related('club').order_by('-date_awarded')
    
    return render(request, 'statisticsrafi/most_awards.html', {
        'players': players_with_awards,
        'clubs': clubs_with_awards,
        'club_awards': club_awards,
    })

def club_rankings(request):
    """FIFA Club World Rankings"""
    rankings = ClubRanking.objects.order_by('rank')
    return render(request, 'statisticsrafi/club_rankings.html', {'rankings': rankings})

# READ - Detail Views
def player_detail(request, player_id):
    """Individual player statistics"""
    player = get_object_or_404(Player, id=player_id)
    stats = PlayerStatistics.objects.filter(player=player)
    awards = Award.objects.filter(player=player)
    
    context = {
        'player': player,
        'stats': stats,
        'awards': awards,
    }
    return render(request, 'statisticsrafi/player_detail.html', context)

# CREATE - Watchlist
@login_required
def add_to_watchlist(request, player_id):
    """Add player to user's watchlist"""
    player = get_object_or_404(Player, id=player_id)
    
    watchlist_item, created = UserWatchlist.objects.get_or_create(
        user=request.user,
        player=player
    )
    
    if created:
        messages.success(request, f'{player.name} added to your watchlist!')
    else:
        messages.info(request, f'{player.name} is already in your watchlist.')
    
    return redirect('statisticsrafi:player_detail', player_id=player_id)

# READ - User Votes
@login_required
def my_watchlist(request):
    """User's voting history"""
    votes = Vote.objects.filter(user=request.user)
    club_votes = ClubVote.objects.filter(user=request.user)
    return render(request, 'statisticsrafi/watchlist.html', {
        'votes': votes,
        'club_votes': club_votes
    })

# DELETE - Watchlist
@login_required
def remove_from_watchlist(request, watchlist_id):
    """Remove player from watchlist"""
    watchlist_item = get_object_or_404(UserWatchlist, id=watchlist_id, user=request.user)
    player_name = watchlist_item.player.name
    watchlist_item.delete()
    messages.success(request, f'{player_name} removed from your watchlist.')
    return redirect('statisticsrafi:my_watchlist')

# UPDATE - Watchlist Notes
@login_required
def update_watchlist_notes(request, watchlist_id):
    """Update notes for a watchlist item"""
    watchlist_item = get_object_or_404(UserWatchlist, id=watchlist_id, user=request.user)
    
    if request.method == 'POST':
        watchlist_item.notes = request.POST.get('notes', '')
        watchlist_item.save()
        messages.success(request, 'Notes updated successfully!')
        return redirect('statisticsrafi:my_watchlist')
    
    return render(request, 'statisticsrafi/edit_watchlist_notes.html', {'item': watchlist_item})

# CREATE - Vote
@login_required
def vote(request, category, season):
    """Vote for Player/Team of Week/Month/Season"""
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        club_id = request.POST.get('club_id')
        week_number = request.POST.get('week_number')
        month_number = request.POST.get('month_number')
        
        try:
            vote_obj, created = Vote.objects.update_or_create(
                user=request.user,
                category=category,
                season=season,
                week_number=week_number,
                month_number=month_number,
                defaults={
                    'player_id': player_id if player_id else None,
                    'club_id': club_id if club_id else None,
                }
            )
            
            if created:
                messages.success(request, 'Vote submitted successfully!')
            else:
                messages.success(request, 'Vote updated successfully!')
                
        except Exception as e:
            messages.error(request, f'Error submitting vote: {str(e)}')
    
    return redirect('statisticsrafi:vote_results', category=category, season=season)

# READ - Vote Results
def vote_results(request, category, season):
    """Display voting results"""
    votes = Vote.objects.filter(category=category, season=season)
    
    if 'PLAYER' in category:
        results = votes.values('player__name', 'player__club__name', 'player__club__logo_url').annotate(
            vote_count=Count('id')
        ).order_by('-vote_count')
    else:
        results = votes.values('club__name', 'club__logo_url').annotate(
            vote_count=Count('id')
        ).order_by('-vote_count')
    
    context = {
        'category': category,
        'season': season,
        'results': results,
    }
    return render(request, 'statisticsrafi/vote_results.html', context)

# Club Comparison
def compare_clubs(request):
    """Compare two clubs statistics"""
    if request.method == 'POST':
        club1_id = request.POST.get('club1_id')
        club2_id = request.POST.get('club2_id')
        season = request.POST.get('season', '2025/26')
        
        club1 = get_object_or_404(Club, id=club1_id)
        club2 = get_object_or_404(Club, id=club2_id)
        
        stats1 = TeamStatistics.objects.filter(club=club1, season=season).first()
        stats2 = TeamStatistics.objects.filter(club=club2, season=season).first()
        
        context = {
            'club1': club1,
            'club2': club2,
            'stats1': stats1,
            'stats2': stats2,
            'season': season,
        }
        return render(request, 'statisticsrafi/club_comparison_result.html', context)
    
    # GET request - show comparison form
    clubs = Club.objects.all()
    return render(request, 'statisticsrafi/compare_clubs.html', {'clubs': clubs})

# Style Guide
def style_guide(request):
    """Design system style guide"""
    return render(request, 'statisticsrafi/style_guide.html')

# Team Statistics Detail
def team_detail(request, club_id):
    """Display detailed statistics for a specific team"""
    club = get_object_or_404(Club, id=club_id)
    team_stats = TeamStatistics.objects.filter(club=club).order_by('-season').first()
    
    # Get club's players
    players = Player.objects.filter(club=club)
    
    # Get club's player statistics for the season
    player_stats = PlayerStatistics.objects.filter(
        player__club=club,
        season=team_stats.season if team_stats else '2025/26'
    ).select_related('player').order_by('-goals')
    
    # Get club rankings
    club_ranking = ClubRanking.objects.filter(club=club).order_by('-ranking_date').first()
    
    # Get club awards
    club_awards = Award.objects.filter(club=club).order_by('-date_awarded')
    
    # Get user's vote status for the current season
    user_has_voted = False
    user_voted_for_this_club = False
    if request.user.is_authenticated:
        user_vote = ClubVote.objects.filter(user=request.user, season='2025/26').first()
        if user_vote:
            user_has_voted = True
            user_voted_for_this_club = user_vote.club == club
    
    context = {
        'club': club,
        'team_stats': team_stats,
        'players': players,
        'player_stats': player_stats,
        'club_ranking': club_ranking,
        'club_awards': club_awards,
        'user_has_voted': user_has_voted,
        'user_voted_for_this_club': user_voted_for_this_club,
    }
    return render(request, 'statisticsrafi/team_detail.html', context)


@login_required
@require_POST
def vote_for_club(request, club_id):
    """Vote for Club of the Season"""
    club = get_object_or_404(Club, id=club_id)
    season = request.POST.get('season', '2025/26')
    
    try:
        # Check if user already voted for this season
        existing_vote = ClubVote.objects.filter(user=request.user, season=season).first()
        
        if existing_vote:
            if existing_vote.club == club:
                return JsonResponse({
                    'status': 'info',
                    'message': f'You have already voted for {club.name} for {season} season.'
                })
            else:
                # Update existing vote
                existing_vote.club = club
                existing_vote.save()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Your vote has been changed to {club.name} for {season} season.'
                })
        else:
            # Create new vote
            ClubVote.objects.create(user=request.user, club=club, season=season)
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully voted for {club.name} for {season} season!'
            })
            
    except IntegrityError:
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your vote.'
        })


@login_required
@require_POST
def delete_vote(request):
    """Delete user's vote for Club of the Season"""
    season = request.POST.get('season', '2025/26')
    
    try:
        # Find and delete user's vote
        user_vote = ClubVote.objects.filter(user=request.user, season=season).first()
        
        if user_vote:
            club_name = user_vote.club.name
            user_vote.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'Your vote for {club_name} has been deleted.'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No vote found to delete.'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while deleting your vote.'
        })


def voting_results(request):
    """Display voting results for Club of the Season"""
    season = request.GET.get('season', '2025/26')
    
    # Get vote counts for each club
    vote_counts = ClubVote.objects.filter(season=season).values('club__name', 'club__league__name', 'club__logo_url').annotate(
        vote_count=Count('id')
    ).order_by('-vote_count')
    
    # Get total votes
    total_votes = ClubVote.objects.filter(season=season).count()
    
    # Get user's current vote
    user_vote = None
    if request.user.is_authenticated:
        user_vote = ClubVote.objects.filter(user=request.user, season=season).first()
    
    context = {
        'vote_counts': vote_counts,
        'total_votes': total_votes,
        'season': season,
        'user_vote': user_vote,
        'seasons': ['2023/24', '2024/25', '2025/26']
    }
    
    return render(request, 'statisticsrafi/vote_results.html', context)