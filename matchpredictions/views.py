from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from .models import Match, Vote, League, Club
from .forms import MatchForm
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
import json


#  Home
def home(request):
    return HttpResponse("<h1>Welcome to PitchPerfect</h1><p><a href='/predictions/'>Go to Match Predictions</a></p>")


#  MAIN PAGE (List matches + filter by league)
def main_view(request):
    leagues = League.objects.exclude(name="Primeira Liga").order_by('name')
    selected_league_id = request.GET.get('league')
    search_query = request.GET.get('search', '').strip()
    filter_type = request.GET.get('filter', 'all')  #  "all" or "my"

    matches = Match.objects.all().order_by('match_date')

    #  League filter
    if selected_league_id:
        matches = matches.filter(league__id=selected_league_id)

    #  Search filter
    if search_query:
        matches = matches.filter(
            Q(home_team__name__icontains=search_query) |
            Q(away_team__name__icontains=search_query)
        )

    #  My Predictions filter
    if filter_type == 'my' and request.user.is_authenticated:
        matches = matches.filter(votes__user=request.user)  #  FIXED HERE
    elif filter_type == 'my' and not request.user.is_authenticated:
        matches = Match.objects.none()  #  avoids exposing all matches to guests

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

    #  Precompute the counts
    total_votes = match.votes.count()
    home_votes = match.votes.filter(prediction="home_win").count()
    draw_votes = match.votes.filter(prediction="draw").count()
    away_votes = match.votes.filter(prediction="away_win").count()

    #  Use existing percentage logic
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




#  USER VOTE
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



#  CREATE MATCH (Admin only)
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


#  UPDATE MATCH (Admin only)
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


#  DELETE MATCH (Admin only)
@user_passes_test(lambda u: u.is_staff)
def match_delete(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        match.delete()
        return redirect('matchpredictions:main')
    return render(request, 'matchpredictions/match_confirm_delete.html', {'match': match})


#  AJAX ENDPOINT – for loading clubs dynamically when league is selected
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

#  JSON ENDPOINT (for Flutter / quicktype)
def show_json_matches(request):
    selected_league_id = request.GET.get('league')
    search_query = request.GET.get('search', '').strip()
    filter_type = request.GET.get('filter', 'all')

    matches = Match.objects.select_related(
        "league", "home_team", "away_team"
    )

    if selected_league_id:
        matches = matches.filter(league__id=selected_league_id)

    if search_query:
        matches = matches.filter(
            Q(home_team__name__icontains=search_query) |
            Q(away_team__name__icontains=search_query)
        )

    if filter_type == 'my' and request.user.is_authenticated:
        matches = matches.filter(votes__user=request.user).distinct()
    elif filter_type == 'my':
        matches = Match.objects.none()

    data = []

    for match in matches:
        # 🔥 THIS IS THE CRITICAL PART
        user_vote = None
        if request.user.is_authenticated:
            vote = match.votes.filter(user=request.user).first()
            if vote:
                user_vote = vote.prediction

        data.append({
            "id": str(match.id),
            "league": {
                "id": match.league.id if match.league else None,
                "name": match.league.name if match.league else None,
            },
            "home_team": {
                "id": match.home_team.id,
                "name": match.home_team.name,
            },
            "away_team": {
                "id": match.away_team.id,
                "name": match.away_team.name,
            },
            "match_date": match.match_date.isoformat(),
            "status": match.status,
            "total_votes": match.total_votes,
            "vote_summary": match.vote_summary,

            # 🔥 REQUIRED FOR FLUTTER VOTE LOCK
            "user_vote": user_vote,
        })

    return JsonResponse(data, safe=False)


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
@require_POST
def vote_match_api(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    prediction = request.POST.get("prediction")

    if prediction not in ["home_win", "away_win", "draw"]:
        return JsonResponse({"error": "Invalid prediction"}, status=400)

    Vote.objects.update_or_create(
        user=request.user,
        match=match,
        defaults={"prediction": prediction},
    )

    return JsonResponse({
        "message": "Vote recorded",
        "vote_summary": match.vote_summary,
        "total_votes": match.total_votes,
    })

@csrf_exempt
@login_required
def delete_vote_api(request, match_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    vote = Vote.objects.filter(
        user=request.user,
        match_id=match_id
    ).first()

    if not vote:
        return JsonResponse({"error": "Vote not found"}, status=404)

    vote.delete()

    match = Match.objects.get(id=match_id)

    return JsonResponse({
        "success": True,
        "total_votes": match.total_votes,
        "vote_summary": match.vote_summary,
    })

@csrf_exempt  # OK because CookieRequest handles auth via session
@staff_member_required
@require_POST
def match_create_api(request):
    try:
        # ✅ CookieRequest sends FORM data, not JSON
        league_id = request.POST.get("league")
        home_team_id = request.POST.get("home_team")
        away_team_id = request.POST.get("away_team")
        match_date = request.POST.get("match_date")
        status = request.POST.get("status", "upcoming")

        if not all([league_id, home_team_id, away_team_id, match_date]):
            return JsonResponse(
                {"status": "error", "message": "Missing required fields"},
                status=400,
            )

        match = Match.objects.create(
            league_id=league_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=match_date,
            status=status,
        )

        return JsonResponse(
            {
                "status": "success",
                "id": str(match.id),
            },
            status=201,
        )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=400,
        )

@login_required
def is_admin(request):
    return JsonResponse({
        "is_admin": request.user.is_staff
    })