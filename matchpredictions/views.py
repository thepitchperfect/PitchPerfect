from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from .models import Match, Vote, League, Club
from .forms import MatchForm
from django.db.models import Q
from django.contrib import messages

# 🏠 Home
def home(request):
    return HttpResponse("<h1>Welcome to PitchPerfect</h1><p><a href='/predictions/'>Go to Match Predictions</a></p>")


# 🟢 MAIN PAGE (List matches + filter by league)
def main_view(request):
    leagues = League.objects.exclude(name="Primeira Liga").order_by('name')
    selected_league_id = request.GET.get('league')
    search_query = request.GET.get('search', '').strip()
    filter_type = request.GET.get('filter', 'all')  # 🆕 "all" or "my"

    matches = Match.objects.all().order_by('match_date')

    # 🏆 League filter
    if selected_league_id:
        matches = matches.filter(league__id=selected_league_id)

    # 🔍 Search filter
    if search_query:
        matches = matches.filter(
            Q(home_team__name__icontains=search_query) |
            Q(away_team__name__icontains=search_query)
        )

    # 💭 My Predictions filter
    if filter_type == 'my' and request.user.is_authenticated:
        matches = matches.filter(votes__user=request.user)  # ✅ FIXED HERE
    elif filter_type == 'my' and not request.user.is_authenticated:
        matches = Match.objects.none()  # ✅ avoids exposing all matches to guests

    return render(request, 'matchpredictions/main.html', {
        'matches': matches.distinct(),
        'leagues': leagues,
        'selected_league_id': selected_league_id,
        'filter_type': filter_type,
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
    return redirect('matchpredictions:match_detail', match_id=match.id)



# 🟡 CREATE MATCH (Admin only)
@user_passes_test(lambda u: u.is_staff)
def match_create(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('matchpredictions:main')
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
            return redirect('matchpredictions:main')
    else:
        form = MatchForm(instance=match)
    return render(request, 'matchpredictions/match_form.html', {'form': form, 'match': match})


# 🔴 DELETE MATCH (Admin only)
@user_passes_test(lambda u: u.is_staff)
def match_delete(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        match.delete()
        return redirect('matchpredictions:main')
    return render(request, 'matchpredictions/match_confirm_delete.html', {'match': match})


# ⚙️ AJAX ENDPOINT – for loading clubs dynamically when league is selected
def load_clubs(request):
    league_id = request.GET.get('league_id')
    clubs = Club.objects.filter(league_id=league_id).order_by('name')
    return JsonResponse(list(clubs.values('id', 'name')), safe=False)


@login_required
def edit_vote(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    vote = Vote.objects.filter(user=request.user, match=match).first()

    if not vote:
        messages.error(request, "You haven’t voted for this match yet.")
        return redirect('matchpredictions:match_detail', match_id=match.id)

    if request.method == "POST":
        prediction = request.POST.get("prediction")
        if prediction in ["home_win", "away_win", "draw"]:
            vote.prediction = prediction
            vote.save()
            messages.success(request, f"Your vote has been updated to '{prediction.replace('_', ' ').title()}'!")
            return redirect('matchpredictions:match_detail', match_id=match.id)

    return render(request, "matchpredictions/edit_vote.html", {
        "match": match,
        "vote": vote,
    })


@login_required
def delete_vote(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    vote = Vote.objects.filter(user=request.user, match=match).first()

    if not vote:
        messages.error(request, "You have no vote to delete.")
        return redirect('matchpredictions:match_detail', match_id=match.id)

    if request.method == "POST":
        vote.delete()
        messages.success(request, "Your vote has been deleted successfully.")
        return redirect('matchpredictions:match_detail', match_id=match.id)

    return render(request, "matchpredictions/delete_vote_confirm.html", {
        "match": match,
    })



