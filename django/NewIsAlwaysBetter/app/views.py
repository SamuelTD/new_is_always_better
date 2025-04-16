from django.shortcuts import render
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
import requests
import numpy as np

# Create your views here.
class HomeView(TemplateView):
    
    template_name = "app/home.html"
    
class IndexView(LoginRequiredMixin, TemplateView):
    
    template_name = "app/index.html"
    login_url = ""
    
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        df = pd.read_csv("allocine_spider_releases.csv")
        df['genre'] = df['genre'].str.split('|')
        df['actors'] = df['actors'].str.split('|')
        df['actors'] = df['actors'].mask(df['actors'].isna(), ['no value'])
        df['nationality'] = df['nationality'].str.split('|')
        df['langage'] = df['langage'].str.split('|')     
        df['directors'] = df['directors'].str.split('|')     
        df['date']= pd.to_datetime(df['date'], errors='coerce')
        df["date"] = df["date"].dt.strftime("%Y-%m-%dT%H:%M:%S")
        df2  = df[["actors", "date", "directors", "editor", "genre", "langage", "length", "nationality", "title"]]
        movies = []
        for index, row in df2.iterrows():
            if row["actors"] == "no value":
                row["actors"] = []
            movies.append(row.to_dict())
        
        response = requests.post("http://api-luvirasa.hte4ayd9gpfjdja0.francecentral.azurecontainer.io/predict",json=movies)
        predictions = response.json()
        predictions = sorted(predictions["predictions"], key=lambda x: x["predicted_affluence"], reverse=True)
        for prediction in predictions:
            prediction["predicted_affluence"] = int(prediction["predicted_affluence"]/2000)
            prediction["picture_url"] = df.loc[df["title"] == prediction["title"], "picture_url"].iloc[0]      
        
        
        img = df["picture_url"].to_list()
        titles = df["title"].to_list()
        synopsis = df["synopsis"].to_list()
        context["movie_list"] = list(zip(img, titles, synopsis))
        context["predictions"] = predictions
        context["figures"] = []
        for x in range(1, 8):
            context["figures"].append(f"fig{x}.png")
        return context
    