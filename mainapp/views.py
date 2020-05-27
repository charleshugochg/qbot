from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

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
            message = "Invalid credentials."
            return HttpResponseRedirect(reverse('login'))

    if not request.user.is_authenticated:
        return render(request, "mainapp/index.html", {"message": None})

    context = {
        "user": request.user
    }

    return render(request, "mainapp/index.html", {"message": context})


def login_view(request):
    return render(request, "mainapp/login.html", {"message": None})


def register_view(request):
    context = {"message": None}

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        user = User.objects.create_user(username, email, password)
        if user is not None:
            user.save()
            context = {"message": "Account creation success!"}

    return render(request, "mainapp/register.html", context)


def logout_view(request):
    logout(request)
    return render(request, "mainapp/index.html", {"message": "Logged out."})