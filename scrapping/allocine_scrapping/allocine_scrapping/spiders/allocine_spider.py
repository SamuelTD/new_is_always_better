import scrapy
from allocine_scrapping.items import FilmItem

class AllocineSpider(scrapy.Spider):
    
    """
    This is a scrapy spider designed to scrap movies from the french website Allociné.
    """
    
    name = "allocine_spider"
    allowed_domains = ["www.allocine.fr"]
    
    #Scraps from 2010 to 2025
    start_urls = ["https://www.allocine.fr/films/decennie-2020/",
                  "https://www.allocine.fr/films/decennie-2010/",
                  "https://www.allocine.fr/films/decennie-2000/",
                  "https://www.allocine.fr/films/decennie-1990/"]
    
    base_url = "https://www.allocine.fr"
    
    def parse(self, response):
        
        #Each page of the list is marked by the following in the url.
        page_string = "?page="
        
        #Get the amount of list pages for the current year/decades.
        max_pg = response.css("div.pagination-item-holder span:last-child::text").get()
        
        #Loop through each page list.
        #Some lists do not have a pagination block, therefore we simply loop through the single page.
        try:
            max_pg = int(max_pg)
        
            # for x in range(1, 6):
            for x in range(1, max_pg+1):
                yield response.follow(response.url+page_string+str(x), callback=self.parse_film_page)
        except:
            yield response.follow(response.url, callback=self.parse_film_page)
  
  
    def parse_film_page(self, response):
        
        #Loop through each film on a list page.
        films = response.css("li.mdl")
        
        for film in films:
            yield response.follow(film.css("a.meta-title-link::attr(href)").get(), callback=self.parse_film)
        
    
    def parse_film(self, film):
        
        #Build the box-office page url
        box_office_url = self.get_box_office_url(film.url)
        
        #Instance the film Item
        f = FilmItem(french_boxoffice = "")
        
        #Get the critics and viewer critic scores
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
        
        try:
            f["date"] = film.css("div.meta-body-item.meta-body-info span.date::text").get().strip()
        except:
            f["date"] = "TBR"
            
        try:
            f["length"] = film.xpath('.//div[@class="meta-body-item meta-body-info"]/text()[normalize-space()]').get().strip()
        except: 
            f["length"] = "N/A"
            
        f["url"] = film.css("a.meta-title-link::attr(href)").get()
        
        if scores != []:
            f["critics_score"] = scores[0]
            f["viewers_score"] = scores[1]
        else:
            f["critics_score"] = "-"
            f["viewers_score"] = "-"
            
        # f["synopsis"] = film.css("div.content-txt::text").get()
        
        f["directors"] = film.css("div.meta-body-item.meta-body-direction span:nth-of-type(2)::text").get()
        
        f['vo_title'] = film.css("div.meta-body-item span.dark-grey::text").get()
        
        #Get the technical chart of a movie and get any useful info.
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
                case "Année de production":
                    if f['date'] == "TBR":
                        f['date'] = "".join(item.css("span.that::text").getall()).strip()
                case _:
                    pass
        
        #If the film does not have a French box-office, it is not returned as it isn't useful.
        if f['french_boxoffice'] != "":        
            yield film.follow(box_office_url, callback=self.parse_box_office, meta={"item": f, "movie_url": film.url})
        
        else:
            return None

    def parse_box_office(self, response):
        
        f = response.meta["item"]
        
        #Some movies have a innacurate first week (probably due to early screenings). 
        #We look at the first two rows (if there are at least two rows) and compare which has the highest tickets sold.
        #We return the higher result.
        titles = response.css("h2::text").getall()        
        if titles[0] == "Box Office France":      
            boxoffice = response.css("td.responsive-table-column.second-col.col-bg::text").getall()
            if len(boxoffice) >= 2:
                if int(boxoffice[0].strip().replace(" ", "")) > int(boxoffice[1].strip().replace(" ", "")):
                    f['french_first_week_boxoffice'] = boxoffice[0].strip()
                else:
                    f['french_first_week_boxoffice'] = boxoffice[1].strip()
            else:
                f['french_first_week_boxoffice'] = boxoffice[0].strip()
            
        else:
            f['french_first_week_boxoffice'] = ""
        
        #If US box office is availlable, scraps it.
        if len(titles) > 1 and titles[1] == "Box Office US":
            boxoffice_us = response.css("tbody")[1]
            f['us_boxoffice'] = boxoffice_us.css("td.responsive-table-column.third-col::text").getall()[-1].strip()
            boxoffice_us = boxoffice_us.css("td.responsive-table-column.second-col.col-bg::text").getall()
            if len(boxoffice_us) >= 2:
                if int(boxoffice_us[0].strip().replace(" ", "")) > int(boxoffice_us[1].strip().replace(" ", "")):
                    f['us_first_week_boxoffice'] = boxoffice_us[0].strip()
                else:
                    f['us_first_week_boxoffice'] = boxoffice_us[1].strip()
            else:
                f['us_first_week_boxoffice'] = boxoffice_us[0].strip()
        else:
            f['us_boxoffice'] = "N/A"
            f['us_first_week_boxoffice'] = "N/A"
            
        casting_url = self.get_casting_url(response.meta["movie_url"])
            
        yield response.follow(casting_url, callback=self.parse_casting_page, meta={"item": f, "movie_url": response.meta["movie_url"]})
        
    
    def parse_casting_page(self, response):
        
        f = response.meta["item"]
        
        #If no casting page exist, return the current movie as is.
        if response.url == response.meta["movie_url"]:
            return f
        
        #Else process the page
        else:
            actors_cards = response.css("section.section.casting-actor a.meta-title-link::text").getall()
            actors_list = response.css("section.section.casting-actor a.item.link::text").getall()
            if len(actors_cards) > 0 or len(actors_list) > 0:
                f['actors'] = ""
                for actor in actors_cards:
                    f['actors'] += actor + '|'
                for actor in actors_list:
                    f['actors'] += actor + '|'
                    
                f['actors'] = f['actors'][:-1]    
                
            directors_cards = response.css("section.section.casting-director a.meta-title-link::text").getall()
            directors_list = response.css("section.section.casting-director a.item.link::text").getall()
            if len(directors_cards) > 0 or len(directors_list) > 0:
                f['directors'] = ""
                for director in directors_cards:
                    f['directors'] += director + '|'
                for director in directors_list:
                    f['directors'] += director + '|'
                    
                f['directors'] = f['directors'][:-1]   
            
        return f
    
    def get_scores(self, response):
        scores = response.css("span.stareval-note::text").getall()
        
        #Some movies can have a critic score but no viewer score.
        if scores != []:
            try:
                return [scores[0], scores[1]]
            except:
                return [scores[0], "-"]

        return []
  
    def get_box_office_url(self, url):
        
        return url.replace("_gen_cfilm=", "-").replace(".html", "/box-office/")
    
    def get_casting_url(self, url):
        
        return url.replace("_gen_cfilm=", "-").replace(".html", "/casting/")

      