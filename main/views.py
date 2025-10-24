import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.shortcuts import render
from .forms import CustomUserCreationForm

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
            
            response = JsonResponse({
                'status': 'success', 
                'message': 'Login successful!',
                'user': {
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role
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
        return render(request, 'login.html')

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
    return render(request, "main.html")
