from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.contrib import messages
from .models import (
    Player, Club, PlayerStatistics, Award, 
    UserWatchlist, Vote, PlayerComparison, ClubRanking, TeamStatistics
)

# READ - List Views
def statistics_home(request):
    """Main statistics dashboard"""
    context = {
        'top_scorers': PlayerStatistics.objects.filter(season='2024/25').order_by('-goals')[:10],
        'top_assisters': PlayerStatistics.objects.filter(season='2024/25').order_by('-assists')[:10],
        'most_clean_sheets': PlayerStatistics.objects.filter(season='2024/25').order_by('-clean_sheets')[:10],
        'club_rankings': ClubRanking.objects.order_by('rank')[:20],
    }
    return render(request, 'statisticsrafi/home.html', context)

def top_scorers(request, season='2024/25'):
    """Top goal scorers"""
    scorers = PlayerStatistics.objects.filter(season=season).order_by('-goals')
    return render(request, 'statisticsrafi/top_scorers.html', {'scorers': scorers, 'season': season})

def top_assisters(request, season='2024/25'):
    """Top assist providers"""
    assisters = PlayerStatistics.objects.filter(season=season).order_by('-assists')
    return render(request, 'statisticsrafi/top_assisters.html', {'assisters': assisters, 'season': season})

def most_clean_sheets(request, season='2024/25'):
    """Most clean sheets (goalkeepers/defenders)"""
    clean_sheets = PlayerStatistics.objects.filter(season=season).order_by('-clean_sheets')
    return render(request, 'statisticsrafi/clean_sheets.html', {'clean_sheets': clean_sheets, 'season': season})

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
    
    return redirect('player_detail', player_id=player_id)

# READ - Watchlist
@login_required
def my_watchlist(request):
    """User's watchlist"""
    watchlist = UserWatchlist.objects.filter(user=request.user)
    return render(request, 'statisticsrafi/watchlist.html', {'watchlist': watchlist})

# DELETE - Watchlist
@login_required
def remove_from_watchlist(request, watchlist_id):
    """Remove player from watchlist"""
    watchlist_item = get_object_or_404(UserWatchlist, id=watchlist_id, user=request.user)
    player_name = watchlist_item.player.name
    watchlist_item.delete()
    messages.success(request, f'{player_name} removed from your watchlist.')
    return redirect('my_watchlist')

# UPDATE - Watchlist Notes
@login_required
def update_watchlist_notes(request, watchlist_id):
    """Update notes for a watchlist item"""
    watchlist_item = get_object_or_404(UserWatchlist, id=watchlist_id, user=request.user)
    
    if request.method == 'POST':
        watchlist_item.notes = request.POST.get('notes', '')
        watchlist_item.save()
        messages.success(request, 'Notes updated successfully!')
        return redirect('my_watchlist')
    
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
    
    return redirect('vote_results', category=category, season=season)

# READ - Vote Results
def vote_results(request, category, season):
    """Display voting results"""
    votes = Vote.objects.filter(category=category, season=season)
    
    if 'PLAYER' in category:
        results = votes.values('player__name', 'player__club__name').annotate(
            vote_count=Count('id')
        ).order_by('-vote_count')
    else:
        results = votes.values('club__name').annotate(
            vote_count=Count('id')
        ).order_by('-vote_count')
    
    context = {
        'category': category,
        'season': season,
        'results': results,
    }
    return render(request, 'statisticsrafi/vote_results.html', context)

# Player Comparison
def compare_players(request):
    """Compare two players statistics"""
    if request.method == 'POST':
        player1_id = request.POST.get('player1_id')
        player2_id = request.POST.get('player2_id')
        season = request.POST.get('season', '2024/25')
        
        player1 = get_object_or_404(Player, id=player1_id)
        player2 = get_object_or_404(Player, id=player2_id)
        
        stats1 = PlayerStatistics.objects.filter(player=player1, season=season).first()
        stats2 = PlayerStatistics.objects.filter(player=player2, season=season).first()
        
        # Save comparison history if user is logged in
        if request.user.is_authenticated:
            PlayerComparison.objects.create(
                user=request.user,
                player1=player1,
                player2=player2,
                season=season
            )
        
        context = {
            'player1': player1,
            'player2': player2,
            'stats1': stats1,
            'stats2': stats2,
            'season': season,
        }
        return render(request, 'statisticsrafi/comparison_result.html', context)
    
    # GET request - show comparison form
    players = Player.objects.all()
    return render(request, 'statisticsrafi/compare_players.html', {'players': players})

@login_required
def my_comparisons(request):
    """User's comparison history"""
    comparisons = PlayerComparison.objects.filter(user=request.user)
    return render(request, 'statisticsrafi/my_comparisons.html', {'comparisons': comparisons})

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
    
    context = {
        'club': club,
        'team_stats': team_stats,
        'players': players,
        'player_stats': player_stats,
        'club_ranking': club_ranking,
        'club_awards': club_awards,
    }
    return render(request, 'statisticsrafi/team_detail.html', context)