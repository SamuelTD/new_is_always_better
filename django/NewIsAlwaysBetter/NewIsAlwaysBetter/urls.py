"""
URL configuration for NewIsAlwaysBetter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from app.views import custom_404_view

# Définition du handler404
handler404 = 'app.views.custom_404_view'

# Pour accéder à la page 404 en mode DEBUG=True
def custom_page_not_found(request):
    return custom_404_view(request, None)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("404/", custom_page_not_found),  # Pour tester en mode DEBUG
    path('', include('app.urls')),
    # path("__reload__/", include("django_browser_reload.urls"))
]