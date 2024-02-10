from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.log_in, name="login"),
    path("reset-password/<int:user_id>", views.reset_password, name="reset-password"),
    path("verify-login/<int:user_id>", views.login_verification, name="verify_login"),
    path("verify-reset/", views.password_verification, name="verify_reset"),
    path("reset/", views.forgot_password, name="reset"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("passwords/", views.passwords, name="passwords"),
    path("cards/", views.cards, name="cards"),
    path("notes/", views.notes, name="notes"),
    path("history/", views.history, name="history"),
    path("settings/", views.settings, name="settings"),
    path("password-generator/", views.password_generator, name="password_generator"),
    path("logout/", views.log_out, name="logout"),
]
