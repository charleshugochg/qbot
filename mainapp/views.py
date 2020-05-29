from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
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


def shop(request, shop_id):
    try:
        shop = Shop.objects.get(pk=shop_id)
    except Shop.DoesNotExist:
        raise Http404("Shop does not exist")
    
    context = {"shop": shop}
    return render(request, "mainapp/shop.html", context)


#####################################################################
# Don't come down Rio

def queue_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: redirect to proper view
        return render(request, 'mainapp/basic_form_ph_no.html')
    else:
        # TODO: validate phone number
        queues = shop.queue_set.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE)
            | Q(phone_number=phone_number, status=Queue.Status.BOOK))
        if not queues:
            queue = shop.queue_set.create(phone_number=phone_number, status=Queue.Status.QUEUE)
        
        # TODO: redirect to proper view
        return HttpResponseRedirect(reverse('shop', args=(shop_id,)))


def book_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: redirect to proper view
        return render(request, 'mainapp/basic_form_ph_no.html')
    else:
        if not 'arrival_time' in request.POST:
            # return error
            return render(request, 'mainapp/basic_form_arrival.html', {'shop_id': shop_id})
        arrival_time = request.POST['arrival_time']
        # TODO: validate phone number
        # TODO: validate arrival time
        queues = shop.queue_set.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE)
            | Q(phone_number=phone_number, status=Queue.Status.BOOK))
        if not queues:
            book = shop.queue_set.create(phone_number=phone_number, status=Queue.Status.BOOK, arrival_time=arrival_time)
        
        # TODO: redirect to proper view
        return HttpResponseRedirect(reverse('shop', args=(shop_id,)))


def cancel_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: return to proper view
        return render(request, 'mainapp/basic_form_ph_no.html')
    else:
        queues = shop.queue_set.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE)
            | Q(phone_number=phone_number, status=Queue.Status.BOOK))
        for q in queues:
            q.status = Queue.Status.CANCEL
            q.save()
            
        # TODO: return to proper view
        return HttpResponseRedirect(reverse('user'))


def user_view(request):
    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: return to proper view
        return render(request, 'mainapp/basic_form_ph_no.html')
    else:
        queues = Queue.objects.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE) 
            | Q(phone_number=phone_number, status=Queue.Status.BOOK)
            | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
            | Q(phone_number=phone_number, status=Queue.Status.SERVING))
        context = {
            'token_list': queues,
            'phone_number': request.session['phone_number']
        }
    return render(request, 'mainapp/basic_user.html', context)


def reg_ph_view(request):
    try:
        phone_number = request.POST['phone_number']
    except KeyError:
        # TODO: change tmp form
        return render(request, 'mainapp/basic_form_ph_no.html')
    else:
        request.session['phone_number'] = phone_number
        return HttpResponseRedirect(reverse('user'))


def get_num_customer(shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    queues = shop.queue_set.filter(Q(status=Queue.Status.QUEUE)
        | Q(status=Queue.Status.BOOK))
    servings = shop.queue_set.filter(Q(status=Queue.Status.SERVING)
        | Q(status=Queue.Status.ONCALL))
    return len(servings), len(queues)

def get_num_priors(shop_id, phone_number):
    """ catch Queue.DoesNotExist """
    shop = get_object_or_404(Shop, pk=shop_id)
    my_queue = shop.queue_set.get(phone_number=phone_number, status=Queue.Status.QUEUE)
    queues = shop.queue_set.filter(queue_date__lt=my_queue.queue_date, status=Queue.Status.QUEUE)
    return len(queues)