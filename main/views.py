import datetime
import traceback
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render
from .forms import CustomUserCreationForm, CustomUserChangeForm

try:
    from club_directories.models import LeaguePick
except ImportError:
    LeaguePick = None

try:
    from forum.models import Post
except ImportError:
    Post = None

try:
    from matchpredictions.models import Vote
except ImportError:
    Vote = None

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Registration successful. Please log in.',
                'redirect_url': reverse('main:login')
            }, status=201)
        else:
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({
                'status': 'error', 
                'errors': errors
            }, status=400)
    else:
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form}) 

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            profpict_url = user.profpict.url if user.profpict else ''

            response = JsonResponse({
                'status': 'success', 
                'message': 'Login successful!',
                'user': {
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role,
                    'profpict': profpict_url 
                },
                'redirect_url': reverse('main:show_main')
            })
            
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({
                'status': 'error', 
                'errors': errors
            }, status=400)
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

@require_POST
def logout_user(request):
    logout(request)
    response = JsonResponse({
        'status': 'success', 
        'message': 'You have been logged out.',
        'redirect_url': reverse('main:login')
    })
    
    response.delete_cookie('last_login')
    return response

def show_main(request):
    return render(request, "main.html", {"full_name": request.user.full_name})

@login_required
def profile(request):
    profile_user = request.user
    
    edit_form = CustomUserChangeForm(instance=profile_user)
    
    league_pick = []
    if LeaguePick:
        league_pick = LeaguePick.objects.filter(user=profile_user).select_related('club')

    user_posts = []
    if Post:
        user_posts = profile_user.forum_posts.all()[:10]

    user_predictions = []
    if Vote:
        user_predictions = profile_user.matchpred_votes.all().select_related(
            'match', 'match__home_team', 'match__away_team'
        )[:10]

    context = {
        'profile_user': profile_user,
        'edit_form': edit_form,
        'league_pick': league_pick,
        'user_posts': user_posts,
        'user_predictions': user_predictions,
    }
    return render(request, 'profile.html', context)

@login_required
@require_POST
def profile_edit(request):
    form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
    
    if form.is_valid():
        user = form.save()
        
        profpict_url = user.profpict.url if user.profpict else ''

        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully!',
            'user': {
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'profpict': profpict_url,
            }
        }, status=200)
    else:
        errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
        return JsonResponse({
            'status': 'error', 
            'errors': errors
        }, status=400)

def show_json(request):
    product_list = LeaguePick.objects.all()
    data = [
        {
            'id': str(product.id),
            'league': product.league.name,
            'club': product.club.name,
            'user': product.user.full_name,
            'username': product.user.username
        }
        for product in product_list
    ]

    return JsonResponse(data, safe=False)

@login_required
def user_activity_api(request):
    try:
        profile_user = request.user

        # --- 1. LEAGUE PICKS ---
        league_picks_data = []
        # Uses related_name='league_picks' from your model
        picks = profile_user.league_picks.select_related('club')
        
        for pick in picks:
            club = pick.club
            league_picks_data.append({
                'id': str(club.id),       # UUID to string
                'name': club.name,
                'logo_url': club.logo_url, # EXACT FIELD NAME
                'founded_year': club.founded_year,
                'desc': getattr(club, 'details', None).description if hasattr(club, 'details') else "", 
                'is_league_pick': True,
            })

        # --- 2. USER POSTS ---
        user_posts_data = []
        # Uses related_name='forum_posts' from your model
        posts = profile_user.forum_posts.all()[:10]

        for post in posts:
            user_posts_data.append({
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'post_type': post.post_type, # 'discussion' or 'news'
                'author': profile_user.username,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat(),
                'clubs': [],    # Simplified for profile
                'images': [],   # Simplified for profile
                'comments': [], # Simplified for profile
            })

        # --- 3. PREDICTIONS ---
        user_predictions_data = []
        # Uses related_name='matchpred_votes' from your model
        votes = profile_user.matchpred_votes.all().select_related('match', 'match__home_team', 'match__away_team')[:10]

        # Helper to make 'home_win' look nicer
        def format_prediction(code, match):
            if code == 'home_win': return f"{match.home_team.name} Win"
            if code == 'away_win': return f"{match.away_team.name} Win"
            if code == 'draw': return "Draw"
            return code

        for vote in votes:
            user_predictions_data.append({
                'id': str(vote.id), # UUID to string
                'match_title': f"{vote.match.home_team.name} vs {vote.match.away_team.name}",
                'voted_for': format_prediction(vote.prediction, vote.match), # EXACT FIELD NAME: prediction
                'match_date': vote.match.match_date.strftime('%Y-%m-%d'),
            })

        data = {
            'username': profile_user.username,
            'league_picks': league_picks_data,
            'user_posts': user_posts_data,
            'user_predictions': user_predictions_data,
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }, status=500)