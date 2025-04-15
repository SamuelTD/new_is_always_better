from .views import HomeView, IndexView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", LoginView.as_view(template_name="app/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("index/", IndexView.as_view(), name="index")
]
