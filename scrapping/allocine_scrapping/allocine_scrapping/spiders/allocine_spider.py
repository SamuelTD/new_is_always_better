import scrapy
from allocine_scrapping.items import FilmItem

class AllocineSpider(scrapy.Spider):
    
    name = "allocine_spider"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/presse/decennie-2020/annee-2024/"]
    current_url = ""
    
    
    def parse(self, response):
        self.current_url = self.start_urls[0]
        page_string = "?page="
        
        max_pg = response.css("div.pagination-item-holder span:last-child::text").get()
        max_pg = int(max_pg)
        
        # for x in range(1, max_pg+1):
        for x in range(1, 2):
            yield response.follow(self.current_url+page_string+str(x), callback=self.parse_film_page)
            
  
    def parse_film_page(self, response):
        films = response.css("li.mdl")
        
        for film in films:
            yield response.follow(film.css("a.meta-title-link::attr(href)").get(), callback=self.parse_film)
        
    
    def parse_film(self, film):
        f = FilmItem()
        scores = self.get_scores(film)
        f["title"] = film.css("div.titlebar-title.titlebar-title-xl::text").get()
        f['genre'] = ""
        for genre in film.css("div.meta-body-item.meta-body-info span.dark-grey-link"):
            f["genre"] += genre.css("::text").get() + '|'
        f['genre'] = f['genre'][:-1]
        f["date"] = film.css("div.meta-body-item.meta-body-info span.date::text").get().strip()
        f["length"] = film.xpath('.//div[@class="meta-body-item meta-body-info"]/text()[normalize-space()]').get().strip()
        f["url"] = film.css("a.meta-title-link::attr(href)").get()
        f["critics_score"] = scores[0]
        f["viewers_score"] = scores[1]
        # f["synopsis"] = film.css("div.content-txt::text").get()
        f["director"] = film.css("div.meta-body-item.meta-body-direction span:nth-of-type(2)::text").get()
        f['vo_title'] = film.css("div.meta-body-item span.dark-grey::text").get()
        tech_chart = film.css("section.section.ovw.ovw-technical div.item")
        for item in tech_chart:
            match item.css("span.what.light::text").get():
                case "Nationalités":
                    f['nationality'] = "".join(item.css("span.that::text").getall()).strip()
                case "Distributeur":
                    f['editor'] = "".join(item.css("span.that::text").getall()).strip()
                case "Box Office France":
                    f['french_boxoffice'] = "".join(item.css("span.that::text").getall()).strip()
                case "Langues":
                    f['langage'] = "".join(item.css("span.that::text").getall()).strip()
                case "N° de Visa":
                    f['french_visa'] = "".join(item.css("span.that::text").getall()).strip()
                case _:
                    pass
                
        return f

    def get_scores(self, response):
        scores = response.css("span.stareval-note::text").getall()
        
        return [scores[0], scores[1]]
  
    #  actors = scrapy.Field()
    # nationality = scrapy.Field()
    # editor = scrapy.Field()
    # french_boxoffice = scrapy.Field()
    # french_first_week_boxoffice = scrapy.Field()
    # langage = scrapy.Field()
    # french_visa = scrapy.Field()
        