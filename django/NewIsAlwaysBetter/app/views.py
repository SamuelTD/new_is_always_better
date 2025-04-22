from django.shortcuts import render
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from app.utils import get_movie_datas
from app.models import Movie


# Create your views here.
class HomeView(TemplateView):
    
    template_name = "app/home.html"
    
class IndexView(LoginRequiredMixin, TemplateView):
    
    template_name = "app/index.html"
    login_url = ""
    
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        img, titles, synopsis, predictions = get_movie_datas()        
        
        context["movie_list"] = list(zip(img, titles, synopsis))
        context["predictions"] = predictions
        context["figures"] = []
        for x in range(1, 13):
            context["figures"].append(f"fig{x}.png")
        return context
    
class WipeTableView(TemplateView):
    
    template_name = "app/delete.html"
    
    def get(self, request, *args, **kwargs):
        Movie.objects.all().delete()
        return super().get(request, *args, **kwargs)