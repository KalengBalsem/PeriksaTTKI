from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from django.contrib import auth
from django.contrib.auth.models import User
from django_ratelimit.decorators import ratelimit
from .models import Chat, UserCorrection
from django.utils import timezone

# google outh imports
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
import os
####

# inferencing language model api
from .model_inference import call_model
import json
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
        if request.POST.get('data_type') == 'user_input':
            user_input = request.POST.get('user_input')
            response = call_model(user_input)
            typo_words = response['typo_words']  # typo words is not used..
            error_words = response['error_words']
            paraphrase = response['paraphrase']
            if getattr(request, 'limited', False):
                return JsonResponse({'typo_words': 'Terlalu Banyak Request (max=5/minute).', 'error_words': '', 'paraphrase': 'Terlalu Banyak Request (max=5/minute).'})
            # registering user input to the database
            chat = Chat(user=request.user, message=user_input, response=response, timestamp=timezone.now())
            chat.save()
            ####
            return JsonResponse({'typo_words': typo_words, 'error_words': error_words, 'paraphrase': paraphrase})
        elif request.POST.get('data_type') == 'user_correction':
            user_correction_data = json.loads(request.POST.get('user_correction'))
            original_word = user_correction_data['original_word']
            user_correction = user_correction_data['user_correction']
            # registering user_correction to the database
            usercorrection = UserCorrection(user=request.user, original_word=original_word, user_correction=user_correction, timestamp=timezone.now())
            usercorrection.save()
            ####
            return HttpResponse(json.dumps('user_correction has successfully stored.'))
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

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)

    # In a real app, I'd also save any new user here to the database. See below for a real example I wrote for Photon Designer.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    request.session['user_data'] = user_data

    return redirect('index')

def logout(request):
    auth.logout(request)
    return redirect('index')