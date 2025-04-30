# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ActorItem(scrapy.Item):
    
    rank = scrapy.Field()
    name = scrapy.Field()
    amount_of_film_played_in = scrapy.Field()
    nationality = scrapy.Field()
    boxoffice_total = scrapy.Field()
    boxoffice_total_first_role = scrapy.Field()
    boxoffice_average = scrapy.Field()
    boxoffice_average_first_role = scrapy.Field()