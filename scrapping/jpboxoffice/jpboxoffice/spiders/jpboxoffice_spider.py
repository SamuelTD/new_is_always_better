import scrapy

# class JpboxSpider(scrapy.Spider):
#     name = "jpbox"
#     allowed_domains = ["jpbox-office.com"]
#     start_urls = ["https://www.jpbox-office.com/top100.php?view=2"]

#     def parse(self, response):
#         # Sélection des liens vers les pages des films
#         film_links = response.css("table tr td a::attr(href)").getall()
#         for link in film_links:
#             if "film.php" in link:  # Vérifie qu'on a bien un lien vers un film
#                 yield response.follow(link, callback=self.parse_film)

#     def parse_film(self, response):
#         yield {
#             "titre": response.css("h1::text").get(),
#             "date_sortie": response.xpath("//td[contains(text(), 'Date de sortie')]/following-sibling::td/text()").get(),
#             "box_office_france": response.xpath("//td[contains(text(), 'Box Office France')]/following-sibling::td/text()").get(),
#             "box_office_monde": response.xpath("//td[contains(text(), 'Box Office Monde')]/following-sibling::td/text()").get(),
#             "genre": response.xpath("//td[contains(text(), 'Genre')]/following-sibling::td/text()").get(),
#             "distributeur": response.xpath("//td[contains(text(), 'Distributeur')]/following-sibling::td/text()").get(),
#             "realisateur": response.xpath("//td[contains(text(), 'Réalisé par')]/following-sibling::td/a/text()").get(),
#             "acteurs": response.xpath("//td[contains(text(), 'Acteurs')]/following-sibling::td//a/text()").getall(),
#        }

class JpboxSpider(scrapy.Spider):
    name = "jpbox"
    allowed_domains = ["jpbox-office.com"]
    start_urls = ["https://www.jpbox-office.com/v9_demarrage.php?view=2"]

    def parse(self, response):
        links = response.css('td.col_poster_titre')
        for link in links:
            title=link.css('::text').get()
        return title
            
