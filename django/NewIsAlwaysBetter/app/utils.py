from datetime import timedelta, date
import pandas as pd
import requests
from app.models import Movie
import os

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

def get_movie_datas() :
    date_to_check = get_next_wednesday()
    img = []
    titles = []
    synopsis = []
    url = []
    predictions = []
    if not Movie.objects.filter(date=date_to_check).exists():
        df = pd.read_csv("allocine_spider_releases.csv")
        df['genre'] = df['genre'].str.split('|')
        df['actors'] = df['actors'].str.split('|')
        df['actors'] = df['actors'].mask(df['actors'].isna(), ['no value'])
        df['directors'] = df['directors'].mask(df['directors'].isna(), ['no value'])
        df['nationality'] = df['nationality'].str.split('|')
        df['langage'] = df['langage'].str.split('|')     
        df['directors'] = df['directors'].str.split('|')     
        df['date']= pd.to_datetime(df['date'], errors='coerce')
        df["date"] = df["date"].dt.strftime("%Y-%m-%dT%H:%M:%S")
        df2  = df[["actors", "date", "directors", "editor", "genre", "langage", "length", "nationality", "title"]]
        movies = []
        movie_items = []
        for (index, row), (index2, row2) in zip(df2.iterrows(), df.iterrows()):
            if row["actors"] == "no value":
                row["actors"] = []
            if row["directors"] == "no value":
                row["directors"] = []
            movie_item = Movie(title = row2["title"], url = row2["url"], picture_url = row2["picture_url"], synopsis = row2["synopsis"],\
                date = date_to_check)
            movies.append(row.to_dict())
            movie_items.append(movie_item)
        
        response = requests.post(os.getenv("API_URL"),json=movies)
        predictions = response.json()
        predictions = sorted(predictions["predictions"], key=lambda x: x["predicted_affluence"], reverse=True)
        for prediction in predictions:
            prediction["predicted_affluence"] = int(prediction["predicted_affluence"]/2000)
            prediction["picture_url"] = df.loc[df["title"] == prediction["title"], "picture_url"].iloc[0]  
            for movie_item in movie_items:
                if movie_item.title == prediction["title"]:
                    movie_item.predicted_affluence = prediction["predicted_affluence"]  
                    break
            
        for movie_item in movie_items:
            movie_item.save()        
    
        img = df["picture_url"].to_list()
        titles = df["title"].to_list()
        synopsis = df["synopsis"].to_list()
        url = df["url"].to_list()
        
    else:
        movies = Movie.objects.filter(date=date_to_check).order_by("-predicted_affluence")        
        for movie in movies:
            img.append(movie.picture_url)
            titles.append(movie.title)
            synopsis.append(movie.synopsis)
            url.append(movie.url)
            predictions.append({"title": movie.title, "predicted_affluence": movie.predicted_affluence, "picture_url": movie.picture_url,\
                "url": movie.url})
    
    return img, titles, synopsis, url, predictions