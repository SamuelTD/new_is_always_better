from .views import HomeView
from django.contrib.auth.views import LoginView
from django.urls import path, reverse_lazy

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", LoginView.as_view(template_name="app/login.html"), name="login")
]
