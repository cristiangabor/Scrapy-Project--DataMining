import scrapy

class YellowpagesItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field()
    title = scrapy.Field()
    adress = scrapy.Field()
    logo = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    phone = scrapy.Field()
