from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.contrib import auth
from django.contrib.auth.models import User
from django_ratelimit.decorators import ratelimit

# inferencing the model
from .model_inference import call_model
####

# Create your views here.
def index(request):
    # i might need to change this part (hardcoded)
    if request.user.is_authenticated:
        return redirect('main')
    else:
        return render(request, 'index.html')
    ####

@ratelimit(key='user_or_ip', rate='5/m', method=['POST'], block=False)
def main(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        if getattr(request, 'limited', False):
            return JsonResponse({'typo_words': 'Too Many Requests (max=5/minute).', 'paraphrase': 'Too Many Requests (max=5/minute).'})
        response = call_model(user_input)
        typo_words = response['typo_words']
        paraphrase = response['paraphrase']
        return JsonResponse({'user_input': user_input, 'typo_words': typo_words, 'paraphrase': paraphrase})
    elif request.user.is_authenticated:
        return render(request, 'main.html')
    else:
        return redirect('index')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, username=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('main')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(email, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('main')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password don\'t match'
            return render(request, 'register.html', {'error_message': error_message})
    else:
        return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('index')