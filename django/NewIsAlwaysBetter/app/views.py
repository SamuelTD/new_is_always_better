from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.utils import get_movie_datas, get_history
from app.models import Movie
from datetime import datetime
import json
import shap
import pickle
import base64
import io
import plotly.io as pio

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
        context["history_json"] = json.dumps(history, default=str)
        for x in range(1, 13):
            context["figures"].append(f"fig{x}.png")
        if self.request.GET.get("content") == "releases":
            context["is_releases"] = True
        if self.request.GET.get("content") == "predictions":
            context["is_predictions"] = True
        if self.request.GET.get("content") == "dashboard":
            context["is_dashboard"] = True
        if self.request.GET.get("content") == "history":
            context["is_history"] = True
        return context
    
class AccountingView(LoginRequiredMixin, TemplateView):
    template_name = "app/accounting.html"
    login_url = ""
    
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        img, titles, synopsis, url, predictions = get_movie_datas()        
        history = get_history()

        # Ajout : enrichir chaque semaine avec total_affluence et total_revenue
        for week in history:
            movie_1_affluence = week["movie_1"].real_affluence if week["movie_1"] else 0
            movie_2_affluence = week["movie_2"].real_affluence if week["movie_2"] else 0
            movie_1_p_affluence = week["movie_1"].predicted_affluence if week["movie_1"] else 0
            movie_2_p_affluence = week["movie_2"].predicted_affluence if week["movie_2"] else 0
            week["total_affluence"] = movie_1_affluence + movie_2_affluence
            week["total_revenue"] = week["total_affluence"] * 10
            week["predicted_total_revenue"] = movie_1_p_affluence + movie_2_p_affluence * 10
            week["benefit"] = week["total_revenue"] - 4900

        history = sorted(history, key=lambda week: datetime.strptime(week["date"], "%d/%m/%Y"))

        context["history"] = history
        return context

    
class WipeTableView(TemplateView):
    
    template_name = "app/delete.html"
    
    def get(self, request, *args, **kwargs):
        Movie.objects.all().delete()
        return super().get(request, *args, **kwargs)

class PredictionView(LoginRequiredMixin, DetailView):
    model = Movie
    template_name = 'app/prediction.html'
    context_object_name = 'movie'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Suppose que ton objet Movie stocke shap_values en base64
        shap_string = self.object.shap_values

        # Désérialiser shap_values
        shap_values = self.deserialize_shap(shap_string)

        # activer plotly pour shap
        shap.initjs()

        # Créer le plot en mode Plotly
        plot = shap.plots.waterfall(shap_values[0], show=False)

        # Convertir en HTML embeddable
        plot_html = pio.to_html(plot, full_html=False)

        context['shap_waterfall_html'] = plot_html

        return context

    @staticmethod
    def deserialize_shap(shap_string):
        print(shap_string)
        shap_bytes = base64.b64decode(shap_string.encode('utf-8'))
        return pickle.loads(shap_bytes)
    

def set_affluence(request, movie_id):
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        movie.real_affluence = int(request.POST.get("real_affluence", 0))
        movie.save()
    return HttpResponseRedirect(f"{reverse('index')}?content=history")