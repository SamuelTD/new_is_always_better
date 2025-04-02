import scrapy
from allocine_scrapping.items import FilmItem

class AllocineSpider(scrapy.Spider):
    
    name = "allocine_spider"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/presse/decennie-2020/annee-2024/"]
    current_url = ""
    
    list_films = []
    
    def parse(self, response):
        
        films = response.css("li.mdl")
        
        for film in films:
            f = FilmItem()
            f["title"] = film.css()
        
        