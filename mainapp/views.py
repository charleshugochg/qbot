from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from .models import Shop, ShopForm

from .models import Shop, Queue

# Created by DEV-B.

def index(request):
    context = {
        "shops": Shop.objects.all(),
    }
    if not request.user.is_authenticated:
        return render(request, "mainapp/index.html", context)

    context["user"] = request.user
    return render(request, "mainapp/index.html", context)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "mainapp/login.html", {"message": "Invalid credentials."})
    return render(request, "mainapp/login.html")


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
    return redirect("index")


def shop(request, shop_id):
    try:
        shop = Shop.objects.get(pk=shop_id)
        in_serving, in_queue = get_num_customer(shop_id)
    except Shop.DoesNotExist:
        raise Http404("Shop does not exist")
    
    context = {
        "shop": shop,
        "in_serving": in_serving,
        "in_queue": in_queue,
    }
    return render(request, "mainapp/shop.html", context)


def shop_profile(request):
    if not request.user.is_authenticated:
        context = {"message": "Please create an owner account!"}
        return render(request, "mainapp/shop_profile.html", context)
    
    user = request.user
    shop = Shop.objects.get(user=request.user)
    if request.method == "POST":
        name = request.POST["name"]
        shop_type = request.POST["shop_type"]
        capacity = request.POST["capacity"]
        phone_number = request.POST["phone_number"]
        address = request.POST["shop_address"]
        logo = request.FILES.get('logoImage', False)
        
        shop.name = name
        shop.shop_type = shop_type
        shop.capacity = capacity
        shop.phone_number = phone_number
        shop.address = address
        shop.logo = logo
        shop.save()
    context = {
        "user": user,
        "shop": shop
    }

    return render(request, "mainapp/shop_profile.html", context)


#####################################################################
# Don't come down Rio

def queue_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: redirect to proper view
        return render(request, 'mainapp/basic_form_ph_no.html', {'ret': reverse('queue', args=(shop_id,))})
    else:
        # TODO: validate phone number
        queues = shop.queue_set.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE)
            | Q(phone_number=phone_number, status=Queue.Status.BOOK)
            | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
            | Q(phone_number=phone_number, status=Queue.Status.SERVING))
        if not queues:
            queue = shop.queue_set.create(phone_number=phone_number, status=Queue.Status.QUEUE)

        # TODO: we could change this job to another
        update_queues(shop_id)
        
        # TODO: redirect to proper view
        return HttpResponseRedirect(reverse('shop', args=(shop_id,)))


def book_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: redirect to proper view
        return render(request, 'mainapp/basic_form_ph_no.html', {'ret': reverse('book', args=(shop_id,))})
    else:
        if not 'arrival_time' in request.POST:
            # return error
            return render(request, 'mainapp/basic_form_arrival.html', {'shop_id': shop_id})
        arrival_time = request.POST['arrival_time']
        # TODO: validate phone number
        # TODO: validate arrival time
        queues = shop.queue_set.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE)
            | Q(phone_number=phone_number, status=Queue.Status.BOOK)
            | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
            | Q(phone_number=phone_number, status=Queue.Status.SERVING))
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
        return render(request, 'mainapp/basic_form_ph_no.html', {'ret': reverse('cancel', args=(shop_id,))})
    else:
        queues = shop.queue_set.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE)
            | Q(phone_number=phone_number, status=Queue.Status.BOOK)
            | Q(phone_number=phone_number, status=Queue.Status.ONCALL))
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
        return render(request, 'mainapp/basic_form_ph_no.html', {'ret': reverse('user')})
    else:
        queues = Queue.objects.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE) 
            | Q(phone_number=phone_number, status=Queue.Status.BOOK)
            | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
            | Q(phone_number=phone_number, status=Queue.Status.SERVING))
        context = {
            'token_list': queues,
            'phone_number': request.session['phone_number'],
            'ret': reverse('user')
        }
    return render(request, 'mainapp/basic_user.html', context)

def success_view(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)

    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: return to proper view
        return render(request, 'mainapp/basic_form_ph_no.html', {'ret': reverse('success', args=(shop_id,))})
    else:
        queues = shop.queue_set.filter(phone_number=phone_number, status=Queue.Status.SERVING)
        for q in queues:
            q.status = Queue.Status.SUCCESS
            q.save()

        # TODO: we could change this job to another
        update_queues(shop_id)
        
        # TODO: redirect to proper view
        return HttpResponseRedirect(reverse('shop', args=(shop_id,)))


def reg_ph_view(request, ret):
    try:
        phone_number = request.POST['phone_number']
    except KeyError:
        # TODO: change tmp form
        return render(request, 'mainapp/basic_form_ph_no.html', ret)
    else:
        request.session['phone_number'] = phone_number
        return HttpResponseRedirect(ret)


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

def update_queues(shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    servings = shop.queue_set.filter(Q(status=Queue.Status.SERVING) | Q(status=Queue.Status.ONCALL))
    num_free_space = shop.capacity - len(servings)
    queues = shop.queue_set.filter(status=Queue.Status.QUEUE).order_by('queue_date')[:num_free_space]
    for q in queues:
        q.status = Queue.Status.ONCALL
        q.save()