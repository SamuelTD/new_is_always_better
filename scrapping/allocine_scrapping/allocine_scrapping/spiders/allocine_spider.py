import scrapy
from allocine_scrapping.items import FilmItem

class AllocineSpider(scrapy.Spider):
    
    name = "allocine_spider"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/presse/decennie-2020/annee-2021/",
                  "https://www.allocine.fr/films/presse/decennie-2020/annee-2022/", 
                  "https://www.allocine.fr/films/presse/decennie-2020/annee-2023/", 
                  "https://www.allocine.fr/films/presse/decennie-2020/annee-2024/",
                  "https://www.allocine.fr/films/presse/decennie-2020/annee-2025/"]
    current_url = ""
    base_url = "https://www.allocine.fr"
    
    def parse(self, response):
        self.current_url = self.start_urls[0]
        page_string = "?page="
        
        max_pg = response.css("div.pagination-item-holder span:last-child::text").get()
        max_pg = int(max_pg)
        
        # for x in range(1, 2):
        for x in range(1, max_pg+1):
            yield response.follow(response.url+page_string+str(x), callback=self.parse_film_page)
            
  
    def parse_film_page(self, response):
        films = response.css("li.mdl")
        
        for film in films:
            yield response.follow(film.css("a.meta-title-link::attr(href)").get(), callback=self.parse_film)
        
    
    def parse_film(self, film):
        
        box_office_url = self.get_box_office_url(film.url)
        
        f = FilmItem()
        scores = self.get_scores(film)
        f["title"] = film.css("div.titlebar-title.titlebar-title-xl::text").get()
        f['genre'] = ""
        for genre in film.css("div.meta-body-item.meta-body-info span.dark-grey-link"):
            f["genre"] += genre.css("::text").get() + '|'
        f['genre'] = f['genre'][:-1]
        
        f['actors'] = ""
        for actor in film.css("div.meta-body-item.meta-body-actor span.dark-grey-link"):
            f['actors'] += actor.css("::text").get() + '|'
        f['actors'] = f['actors'][:-1]
        
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
                case "Nationalités" | "Nationalité":
                    f['nationality'] = "".join(item.css("span.that span::text").getall()).strip()                   
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
                
        yield film.follow(box_office_url, callback=self.parse_box_office, meta={"item": f})

    def parse_box_office(self, response):
        f = response.meta["item"]
        f['french_first_week_boxoffice'] = response.css("td.responsive-table-column.second-col.col-bg::text").get().strip()
        return f
    
    def get_scores(self, response):
        scores = response.css("span.stareval-note::text").getall()
        
        return [scores[0], scores[1]]
  
    def get_box_office_url(self, url):
        
        return url.replace("_gen_cfilm=", "-").replace(".html", "/box-office/")

      