from django.shortcuts import render
from django.views.generic import TemplateView, ListView, View

# Create your views here.
class HomeView(TemplateView):
    
    template_name = "app/home.html"
    
class IndexView(TemplateView):
    
    template_name = "app/index.html"