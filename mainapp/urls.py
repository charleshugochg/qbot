from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("shop/<int:shop_id>/", views.shop, name="shop"),
    path("shop_profile", views.shop_profile, name="shop_profile"),
    #ex: /1/queue
    path("queue/<int:shop_id>/", views.queue_view, name="queue"),
    #ex: /1/book
    path("book/<int:shop_id>/", views.book_view, name="book"),
    #ex: /1/cancel
    path("cancel/<int:shop_id>/", views.cancel_view, name="cancel"),
    #ex: /user
    path("user/", views.user_view, name="user"),
    path("regph/", views.reg_ph_view, name="register_phone_number"),
]
