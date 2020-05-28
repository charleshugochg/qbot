from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Shop

# Created by DEV-B.

def index(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "mainapp/login.html", {"message": "Invalid credentials."})

    if not request.user.is_authenticated:
        return render(request, "mainapp/index.html", {"message": None})

    context = {
        "user": request.user,
        "shops": Shop.objects.all(),
    }

    return render(request, "mainapp/index.html", context)


def login_view(request):
    return render(request, "mainapp/login.html", {"message": None})


def register_view(request):
    context = {"message": None}

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        
        # TODO: add some verifications here.
        if username and email and password:
            user = User.objects.create_user(username, email, password)
            user.save()
            context = {"message": "Account creation success!"}
        else:
            context = {"message": "Invalid credentials."}

    return render(request, "mainapp/register.html", context)


def logout_view(request):
    logout(request)
    return render(request, "mainapp/index.html", {"message": "Logged out."})