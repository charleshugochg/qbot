from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("shop_list/", views.shop_list, name="shop_list"),
    path("shop/<int:shop_id>/", views.shop, name="shop"),
    path("shop_profile/", views.shop_profile, name="shop_profile"),
    #ex: /queue/1
    path("queue/<int:shop_id>/", views.queue_view, name="queue"),
    #ex: /book/1
    path("book/<int:shop_id>/", views.book_view, name="book"),
    #ex: /cancel/1
    path("cancel/<int:shop_id>/", views.cancel_view, name="cancel"),
    #ex: /user
    path("user/", views.user_view, name="user"),
    #ex: /regph
    path("regph/ret=<path:ret>/", views.reg_ph_view, name="register_phone_number"),
    #ex: /success/1
    path("success/<int:shop_id>/", views.success_view, name="success"),
    #ex: /auth_token/075194d3-6885-417e-a8a8-6c931e272f00
    path("auth_token/", views.auth_token_view, name="auth_token"),
]
