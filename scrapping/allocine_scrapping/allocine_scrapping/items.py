# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FilmItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    vo_title = scrapy.Field()
    date = scrapy.Field()
    genre = scrapy.Field()
    length = scrapy.Field()
    url = scrapy.Field()
    critics_score = scrapy.Field()
    viewers_score = scrapy.Field()
    # synopsis = scrapy.Field()
    director = scrapy.Field()
    actors = scrapy.Field()
    nationality = scrapy.Field()
    editor = scrapy.Field()
    french_boxoffice = scrapy.Field()
    french_first_week_boxoffice = scrapy.Field()
    langage = scrapy.Field()
    french_visa = scrapy.Field()
    pass
