from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from app.utils import get_movie_datas, get_history
from app.models import Movie
from datetime import datetime

# Create your views here.
class HomeView(TemplateView):
    
    template_name = "app/home.html"
    
class IndexView(LoginRequiredMixin, TemplateView):
    
    template_name = "app/index.html"
    login_url = ""
    
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        img, titles, synopsis, url, predictions = get_movie_datas()        
        history = get_history()
        
        context["movie_list"] = list(zip(img, titles, synopsis, url))
        context["predictions"] = predictions
        context["history"] = history
        context["figures"] = []
        for x in range(1, 13):
            context["figures"].append(f"fig{x}.png")
        if self.request.GET.get("content") == "history":
            context["is_history"] = True
        return context
    
class WipeTableView(TemplateView):
    
    template_name = "app/delete.html"
    
    def get(self, request, *args, **kwargs):
        Movie.objects.all().delete()
        return super().get(request, *args, **kwargs)


def set_affluence(request, movie_id):
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        movie.real_affluence = int(request.POST.get("real_affluence", 0))
        movie.save()
    return HttpResponseRedirect(f"{reverse('index')}?content=history")