import scrapy
from jpboxoffice.items import ActorItem

class JpboxSpider(scrapy.Spider):
    name = "JpboxSpider"
    allowed_domains = ["jpbox-office.com"]
    start_urls = ["https://jpbox-office.com/bigacteurs.php?tri=1&limite=0&view=2&filtre=0&filtre2=0"]

    def parse(self, response):
        limit = 0
        
        while limit < 1000:
            yield response.follow(url=f"https://jpbox-office.com/bigacteurs.php?tri=1&limite={limit}&view=2&filtre=0&filtre2=0", callback=self.parse_page)
            limit += 25
    
    def parse_page(self, response):
        
        if response.css("div.bloc_infos_center.tablesmall1b::text").get() == "Aucune donnée disponible pour cette année.":
            return
        else:
            rows = response.css("table")[1]
            rows = rows.css("tr")
            for row in rows:
                if row.css("td.celluletitre").get() != None :
                    continue
                else:
                    a = ActorItem()
                    a['rank'] = row.css("div.compteur::text").get()
                    a['name'] = row.css("td h3 a::text").get()
                    a['amount_of_film_played_in'] = row.css("h3::text").getall()[0]
                    a['nationality'] = row.css("h3::text").getall()[1]
                    a['boxoffice_total'] = row.css("td.col_poster_contenu_majeur::text").getall()[0]
                    a['boxoffice_total_first_role'] = row.css("td.col_poster_contenu::text").getall()[0]
                    a['boxoffice_average'] = row.css("td.col_poster_contenu_majeur::text").getall()[1]
                    a['boxoffice_average_first_role'] = row.css("td.col_poster_contenu::text").getall()[1]
                    yield a
            