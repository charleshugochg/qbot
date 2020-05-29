from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Shop

from .models import Shop, Queue

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

    context = {
        "shops": Shop.objects.all(),
    }
    if not request.user.is_authenticated:
        return render(request, "mainapp/index.html", context)

    context["user"] = request.user
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


#####################################################################
# Don't come down Rio

def queue_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.POST['phone_number']
    except KeyError:
        # TODO: redirect to proper view
        return render(request, 'mainapp/basic_form_ph_no.html', {'shop_id': shop_id})
    else:
        # TODO: validate phone number
        queue = shop.queue_set.filter(phone_number=phone_number, status=Queue.Status.QUEUE)
        if not queue:
            queue = shop.queue_set.create(phone_number=phone_number, status=Queue.Status.QUEUE)
        request.session['phone_number'] = phone_number
        # TODO: redirect to proper view
        return HttpResponseRedirect(reverse('', args=(shop_id,)))