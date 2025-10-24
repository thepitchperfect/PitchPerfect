from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from .models import Match, Vote, League, Club
from .forms import MatchForm
from django.db.models import Q




# 🏠 Home
def home(request):
    return HttpResponse("<h1>Welcome to PitchPerfect</h1><p><a href='/predictions/'>Go to Match Predictions</a></p>")


# 🟢 MAIN PAGE (List matches + filter by league)
def main_view(request):
    leagues = League.objects.exclude(name="Primeira Liga").order_by('name')
    selected_league_id = request.GET.get('league')
    search_query = request.GET.get('search', '').strip()

    matches = Match.objects.all().order_by('match_date')

    if selected_league_id:
        matches = matches.filter(league__id=selected_league_id)
    if search_query:
        matches = matches.filter(
            Q(home_team__name__icontains=search_query) |
            Q(away_team__name__icontains=search_query)
        )

    return render(request, 'matchpredictions/main.html', {
        'matches': matches,
        'leagues': leagues,
        'selected_league_id': selected_league_id,
    })


# 🔵 DETAIL PAGE (Voting)
def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    user_vote = None

    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(user=request.user, match=match).first()

    # 🧮 Precompute the counts
    total_votes = match.votes.count()
    home_votes = match.votes.filter(prediction="home_win").count()
    draw_votes = match.votes.filter(prediction="draw").count()
    away_votes = match.votes.filter(prediction="away_win").count()

    # 🧠 Use existing percentage logic
    vote_summary = match.vote_summary

    return render(request, 'matchpredictions/match_detail.html', {
        'match': match,
        'user_vote': user_vote,
        'vote_summary': vote_summary,
        'total_votes': total_votes,
        'home_votes': home_votes,
        'draw_votes': draw_votes,
        'away_votes': away_votes,
    })




# 🗳️ USER VOTE
@login_required
def vote_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    if request.method == "POST":
        prediction = request.POST.get("prediction")

        if prediction in ["home_win", "away_win", "draw"]:
            Vote.objects.update_or_create(
                user=request.user,
                match=match,
                defaults={
                    "prediction": prediction,
                }
            )
    return redirect('match_detail', match_id=match.id)



# 🟡 CREATE MATCH (Admin only)
@user_passes_test(lambda u: u.is_staff)
def match_create(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = MatchForm()
    return render(request, 'matchpredictions/match_form.html', {'form': form})


# 🟠 UPDATE MATCH (Admin only)
@user_passes_test(lambda u: u.is_staff)
def match_update(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = MatchForm(instance=match)
    return render(request, 'matchpredictions/match_form.html', {'form': form, 'match': match})


# 🔴 DELETE MATCH (Admin only)
@user_passes_test(lambda u: u.is_staff)
def match_delete(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        match.delete()
        return redirect('main')
    return render(request, 'matchpredictions/match_confirm_delete.html', {'match': match})


# ⚙️ AJAX ENDPOINT – for loading clubs dynamically when league is selected
def load_clubs(request):
    league_id = request.GET.get('league_id')
    clubs = Club.objects.filter(league_id=league_id).order_by('name')
    return JsonResponse(list(clubs.values('id', 'name')), safe=False)


