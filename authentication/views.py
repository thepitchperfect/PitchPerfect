from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from main.models import CustomUser
import json

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
        except:
            username = request.POST.get('username')
            password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return JsonResponse({
                    "status": True,
                    "message": "Login successful!",
                    "username": user.username,
                    "is_staff": user.is_staff, 
                }, status=200)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Login failed, account is disabled."
                }, status=401)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, please check your username or password."
            }, status=401)
            
    return JsonResponse({'status': False, 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']
        email = data['email']
        full_name = data['full_name']

        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        user = CustomUser.objects.create_user(username=username, password=password1, email=email, full_name=full_name)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
    
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)
    
@csrf_exempt
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)

@login_required
def profile_json(request):
    user = request.user
    
    profpict_url = ''
    if hasattr(user, 'profpict') and user.profpict:
        profpict_url = user.profpict.url

    full_name = getattr(user, 'full_name', user.username)
    role = getattr(user, 'role', 'user')

    data = {
        'id': user.id,
        'username': user.username,
        'full_name': full_name,
        'email': user.email,
        'profpict': profpict_url,
        'role': role,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
    }
    
    return JsonResponse([data], safe=False)

@login_required
@csrf_exempt
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        
        # Capture the data from request.POST (not json.loads)
        # We use .get() with the current value as fallback so we don't wipe data if it's missing
        new_name = request.POST.get('full_name', user.full_name)
        new_email = request.POST.get('email', user.email)
        
        # Update fields
        user.full_name = new_name
        user.email = new_email
        
        # Handle Image Upload (request.FILES)
        if 'profpict' in request.FILES:
            user.profpict = request.FILES['profpict']
            
        user.save()

        # Build the response
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

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)