from collections import defaultdict
from datetime import timedelta, date
import pandas as pd
import requests
from app.models import Movie
import os

def get_week_start(date):
    # Align each date to its release Wednesday
    return date - timedelta(days=(date.weekday() - 2) % 7)  # 2 = Wednesday

def get_history():

    # Get all movies with predictions
    movies = Movie.objects.exclude(predicted_affluence=None).order_by('date')

    # Group by release week (each Wednesday)
    weekly_groups = defaultdict(list)

    for movie in movies:
        week = get_week_start(movie.date)
        weekly_groups[week].append(movie)

    # Get top 2 by prediction per week
    top_movies_by_week = []

    for week, group in weekly_groups.items():
        sorted_group = sorted(group, key=lambda m: m.predicted_affluence, reverse=True)
        top_two = sorted_group[:2]

        # Build dictionary
        entry = {
            "date": week.strftime("%d/%m/%Y"),
            "movie_1": top_two[0] if len(top_two) > 0 else None,
            "movie_2": top_two[1] if len(top_two) > 1 else None,
        }
        top_movies_by_week.append(entry)
    
    return top_movies_by_week[::-1]

def get_next_wednesday():
    today = date.today()
    # In Python's weekday convention, Monday is 0 and Sunday is 6.
    # Wednesday is represented by 2.
    wednesday = 2
    # Calculate how many days until the next Wednesday.
    days_ahead = (wednesday - today.weekday() + 7) % 7
    # If today is Wednesday, we want the next Wednesday (7 days ahead)
    if days_ahead == 0:
        days_ahead = 7
    next_wed = today + timedelta(days=days_ahead)
    return next_wed

def get_movie_datas(force_date: date = None) :
    
    if not force_date:
        date_to_check = get_next_wednesday()
    else:
        date_to_check = force_date
        
    img = []
    titles = []
    synopsis = []
    url = []
    predictions = []
    
    movies = Movie.objects.filter(date=date_to_check).order_by("-predicted_affluence")        
    for movie in movies:
        img.append(movie.picture_url)
        titles.append(movie.title)
        synopsis.append(movie.synopsis)
        url.append(movie.url)
        predictions.append({"title": movie.title, "predicted_affluence": movie.predicted_affluence, "predicted_affluence_2": movie.predicted_affluence_2, \
            "shap_values": movie.shap_values, "shap_values_2": movie.shap_values_2, "picture_url": movie.picture_url,\
            "url": movie.url})
    
    for i in range(len(synopsis)):
        if len(synopsis[i]) > 200:
            synopsis[i] = synopsis[i][:197] + "..."
    
    return img, titles, synopsis, url, predictions