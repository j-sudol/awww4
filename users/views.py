from django.shortcuts import render
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate
from .forms import UserLoginForm
from django.contrib.auth import logout
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()

            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'register_form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'login_form': form})

def user_logout(request):
    logout(request)
    return redirect('login')