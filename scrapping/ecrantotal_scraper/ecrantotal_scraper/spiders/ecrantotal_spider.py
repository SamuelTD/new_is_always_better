import scrapy
from ecrantotal_scraper.items import EcrantotalScraperItem


class ecrantotalSpider(scrapy.Spider):
    name='et_spider'
    allowed_domains = ["ecran-total.fr"]
    start_urls = ["https://ecran-total.fr/calendrier/"]
    current_url = ""
    base_url = "https://ecran-total.fr/"

    def parse(self, response):
        list_films = []

        week_programmation = response.css("div.date-list")
        for week in week_programmation:
            date=week.css("h2.font--serif.color--primary.date-separator::text").get()
            films_list = week.css("div.film-card.production.flex")
            for film in films_list:
                item = EcrantotalScraperItem()
                item["date"]=date
                item["title"]= film.css("div.titre h3::text").get()
                item["genre"]= film.css("p.small.genre::text").get()
                list_films.append(item)
        
        return list_films

