from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from .models import Shop

from .models import Shop, Queue

import re

# Created by DEV-B.

def index(request):
    if not request.user.is_authenticated:
        phone = request.session.get('phone_number')
        if phone:
            context = {
                "phone_number": phone,
                "token": get_most_important_token(phone)
                }
            return render(request, "mainapp/index.html", context)
        return render(request, "mainapp/first_time.html")

    shop = Shop.objects.get(user=request.user)
    in_serving, in_queue = get_num_customer(shop.id)
    context = {
        "user": request.user,
        "shop": shop,
        "in_serving": in_serving,
        "in_queue": in_queue,
    }
    
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
            return render(request, "mainapp/login.html", {"message": "Username or password incorrect!"})
    return render(request, "mainapp/login.html")


def register_view(request):
    context = {"message": None}

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        shop_name = request.POST["shop_name"]
        
        # TODO: add some verifications here.
        try:
            user = User.objects.create_user(username, email, password)
            shop = Shop.objects.create(user=user, name=shop_name)
            user.save()
            context = {
                "success": True,
                "message": "Account creation success! Redirect to shop profile."
                }
        except:
            context = {"message": "Please try different username."}

    return render(request, "mainapp/register.html", context)


def logout_view(request):
    logout(request)
    return redirect("index")


def shop_list(request):
    shops = [
        {
            'id': s.id,
            'logo': s.logo,
            'name': s.name,
            'address': s.address,
            'capacity': s.capacity,
            'num_in_queue': get_num_customer(s.id)[1]
        }
        for s in Shop.objects.all()
    ]
    context = {
        "shops": shops,
    }
    return render(request, "mainapp/shop_list.html", context)


def search_result(request):
    text = request.POST.get("search-value")
    ret = request.POST.get("path") or 'index'
    print(text, ret)
    if not text:
        return redirect(ret)
    text = re.escape(text) # make sure there are not regex specials
    context = {
        "shops": Shop.objects.filter(name__iregex=r"(^|\s)%s" % text),
        "value": text,
        "return_path": ret
        }
    return render(request, "mainapp/search_result.html", context)


def shop(request, shop_id):
    try:
        shop = Shop.objects.get(pk=shop_id)
        in_serving, in_queue = get_num_customer(shop_id)
        # phone_number = request.session['phone_number']
        # status, num_priors = get_customer_status(shop_id, phone_number)
    except Shop.DoesNotExist:
        raise Http404("Shop does not exist")
    # except KeyError:
    #     message = "You need to login first."
    # except Queue.DoesNotExist:
    #     message = "You can join the queue."
    # else:
    #     message = f"Your status {status} and there is {num_priors} ppl in front of you"
    
    context = {
        "shop": shop,
        "in_serving": in_serving,
        "in_queue": in_queue,
        # "message": message
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
        shop.name = name
        shop.shop_type = shop_type
        shop.capacity = capacity
        shop.phone_number = phone_number
        shop.address = address

        logo = request.FILES.get('logoImage', False)
        print(logo)
        if logo:
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
        return HttpResponseRedirect(reverse('tokens', args=()))


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

        # TODO: we could change this job to another
        update_queues(shop_id)
            
        # TODO: return to proper view
        return HttpResponseRedirect(reverse('tokens'))


def tokens_view(request):
    try:
        phone_number = request.session['phone_number']
    except KeyError:
        # TODO: return to proper view
        return render(request, 'mainapp/basic_form_ph_no.html', {'ret': reverse('tokens')})
    else:
        queues = Queue.objects.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE) 
            | Q(phone_number=phone_number, status=Queue.Status.BOOK)
            | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
            | Q(phone_number=phone_number, status=Queue.Status.SERVING))
        tokens = [
            {
                'id': q.token_id,
                'shop_name': q.shop.name,
                'shop_id': q.shop.id,
                'queue_id': q.id,
                'on_call': q.status == Queue.Status.ONCALL,
                'status': {
                    Queue.Status.QUEUE: "Waiting",
                    Queue.Status.BOOK: "Booked",
                    Queue.Status.ONCALL: "Calling",
                    Queue.Status.SERVING: "Serving",
                }[q.status],
            }
            for q in queues
        ]

        context = {
            'token_list': tokens,
            'phone_number': request.session['phone_number'],
            'ret': reverse('tokens')
        }
    return render(request, 'mainapp/tokens.html', context)

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


def register_phone_view(request, ret):
    try:
        phone_number = request.POST['phone_number']
    except KeyError:
        # TODO: change tmp form
        return render(request, 'mainapp/basic_form_ph_no.html', {'ret': ret})
    else:
        request.session['phone_number'] = phone_number
        return HttpResponseRedirect(ret)

def auth_token_view(request):
    if not request.user.is_authenticated:
        context = {"error": "Please create an owner account!"}
        return render(request, "mainapp/auth_token.html", context)

    user = request.user
    shop = Shop.objects.get(user=request.user)

    if not request.method == 'POST':
        context = {'shop': shop}
        return render(request, "mainapp/auth_token.html", context)
    if len(request.POST['token_id']) == 0:
        context = {'shop': shop, 'error': "Empty input!"}
        return render(request, "mainapp/auth_token.html", context)

    try:
        token_id = request.POST['token_id']
        # TODO: validate token_id
        queue = shop.queue_set.get(token_id=token_id, status=Queue.Status.ONCALL)
    except KeyError:
        raise Http404("No token found!")
    except Queue.DoesNotExist:
        context = {
            "token_id": token_id,
            "message": "Invalid!",
            "denied":True,
        }
        return render(request, "mainapp/auth_status.html", context)
    else:
        context = {
            "token_id": token_id,
            "message": "Success!"
        }
        queue.status = Queue.Status.SERVING
        queue.save()

        # TODO: we could change this job to another
        update_queues(shop.id)

        return render(request, "mainapp/auth_status.html", context)

def qr_view(request, token_id):
    if len(token_id) == 0:
        context = {'error': "No token found!"}
        return render(request, 'mainapp/qr_view.html', context)

    context = {
        'token_id': token_id
    }
    return render(request, 'mainapp/qr_view.html', context)

## Write views up
## Helper functions
def get_most_important_token(phone_number):
    token = {}
    # TODO: validate phone number
    CASE_SQL = '(case when status="ONCALL" then 1 when status="QUEUE" then 2 when status="BOOK" then 3 when status="SERVING" then 4 end)'
    queues = Queue.objects.filter(Q(phone_number=phone_number, status=Queue.Status.QUEUE) 
        | Q(phone_number=phone_number, status=Queue.Status.BOOK)
        | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
        | Q(phone_number=phone_number, status=Queue.Status.SERVING)).extra(
            select={'status_order': CASE_SQL}, 
            order_by=['status_order']
        )
    if queues:
        token = {
            'queue_id': queues[0].id,
            'shop_name': queues[0].shop.name,
            'on_call': queues[0].status == Queue.Status.ONCALL,
            'status': {
                Queue.Status.QUEUE: "Waiting",
                Queue.Status.BOOK: "Booked",
                Queue.Status.ONCALL: "Calling",
                Queue.Status.SERVING: "Serving",
            }[queues[0].status]
        }
    return token

def get_num_customer(shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    queues = shop.queue_set.filter(Q(status=Queue.Status.QUEUE)
        | Q(status=Queue.Status.BOOK))
    servings = shop.queue_set.filter(Q(status=Queue.Status.SERVING)
        | Q(status=Queue.Status.ONCALL))
    return len(servings), len(queues)

def get_customer_status(shop_id, phone_number):
    """ 
    Return:
        Queue.Status, len(list_of_prior)
    Note:
        catch Queue.DoesNotExist 
    """
    shop = get_object_or_404(Shop, pk=shop_id)
    my_queue = shop.queue_set.get(Q(phone_number=phone_number, status=Queue.Status.QUEUE)
        | Q(phone_number=phone_number, status=Queue.Status.BOOK)
        | Q(phone_number=phone_number, status=Queue.Status.ONCALL)
        | Q(phone_number=phone_number, status=Queue.Status.SERVING))
    queues = shop.queue_set.filter(queue_date__lt=my_queue.queue_date, status=Queue.Status.QUEUE)
    return my_queue.status, len(queues)

def update_queues(shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    servings = shop.queue_set.filter(Q(status=Queue.Status.SERVING) | Q(status=Queue.Status.ONCALL))
    num_free_space = shop.capacity - len(servings)
    queues = shop.queue_set.filter(status=Queue.Status.QUEUE).order_by('queue_date')[:num_free_space]
    for q in queues:
        q.status = Queue.Status.ONCALL
        q.save()