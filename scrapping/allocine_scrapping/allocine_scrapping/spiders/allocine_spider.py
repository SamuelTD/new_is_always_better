import scrapy
from allocine_scrapping.items import FilmItem

class AllocineSpider(scrapy.Spider):
    
    """
    This is a scrapy spider designed to scrap movies from the french website Allociné.
    """
    
    name = "allocine_spider"
    allowed_domains = ["www.allocine.fr"]
    
    #Scraps from 2010 to 2025
    start_urls = ["https://www.allocine.fr/films/decennie-2000/",
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
        
            # for x in range(1, 11):
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
            f["length"] = "0"
            
        f["url"] = film.css("a.meta-title-link::attr(href)").get()
        
        if scores != []:
            f["critics_score"] = scores[0]
            f["viewers_score"] = scores[1]
        else:
            f["critics_score"] = "-"
            f["viewers_score"] = "-"
            
        # f["synopsis"] = film.css("div.content-txt::text").get()
        
        f["director"] = film.css("div.meta-body-item.meta-body-direction span:nth-of-type(2)::text").get()
        
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
                case _:
                    pass
        
        #If the film does not have a French box-office, it is not returned as it isn't useful.
        if f['french_boxoffice'] != "":        
            yield film.follow(box_office_url, callback=self.parse_box_office, meta={"item": f})
        
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

      