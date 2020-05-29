from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("shop/<int:shop_id>/", views.shop, name="shop"),
    #ex: /1/queue
    path("<int:shop_id>/queue/", views.queue_view, name="queue"),
    #ex: /1/book
    path("<int:shop_id>/book/", views.book_view, name="book"),
    #ex: /1/cancel
    path("<int:shop_id>/cancel/", views.cancel_view, name="cancel"),
    #ex: /tokens
    path("tokens", views.tokens_view, name="tokens"),
]
