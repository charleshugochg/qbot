from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Q
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
<<<<<<< HEAD
=======


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
        book = shop.queue_set.filter(phone_number=phone_number, status=Queue.Status.BOOK)
        if not queue and not book:
            queue = shop.queue_set.create(phone_number=phone_number, status=Queue.Status.QUEUE)
        request.session['phone_number'] = phone_number
        # TODO: redirect to proper view
        return HttpResponseRedirect(reverse('index', args=()))


def book_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.POST['phone_number']
        arrival_time = request.POST['arrival_time']
    except KeyError:
        # TODO: redirect to proper view
        return render(request, 'mainapp/basic_form_book.html', {'shop_id': shop_id})
    else:
        # TODO: validate phone number
        # TODO: validate arrival time
        queue = shop.queue_set.filter(phone_number=phone_number, status=Queue.Status.QUEUE)
        book = shop.queue_set.filter(phone_number=phone_number, status=Queue.Status.BOOK)
        if not book and not queue:
            book = shop.queue_set.create(phone_number=phone_number, status=Queue.Status.BOOK, arrival_time=arrival_time)
        request.session['phone_number'] = phone_number
        # TODO: redirect to proper view
        return HttpResponseRedirect(reverse('index', args=()))


def cancel_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.POST['phone_number']
    except KeyError:
        # TODO: return to proper view
        return HttpResponseRedirect(reverse('index'))
    else:
        queues = shop.queue_set.filter(phone_number=phone_number, status=Queue.Status.QUEUE)
        books = shop.queue_set.filter(phone_number=phone_number, status=Queue.Status.BOOK)
        for q in queues:
            q.status = Queue.Status.CANCEL
            q.save()
        for b in books:
            b.status = Queue.Status.CANCEL
            b.save()
        try:
            del request.session['phone_number']
        except KeyError:
            pass
        # TODO: return to proper view
        return HttpResponseRedirect(reverse('index'))


def tokens_view(request):
    try:
        phone_number = request.POST['phone_number']
    except KeyError:
        # TODO: return to proper view
        return HttpResponseRedirect(reverse('index'))
    else:
        queues = Queue.objects.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE) 
            | Q(phone_number=phone_number, status=Queue.Status.BOOK)
            | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
            | Q(phone_number=phone_number, status=Queue.Status.SERVING))
    return render(request, 'mainapp/basic_list_token.html', {'token_list': queues})
>>>>>>> 0c6bbe9c3c9b5e5a3ac2d7e1846b2d9749e3fa7c
