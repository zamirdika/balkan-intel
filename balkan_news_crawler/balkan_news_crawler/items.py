import scrapy

class BalkanNewsCrawlerItem(scrapy.Item):
    # Core fields gathered during the scraping process
    source_domain = scrapy.Field()
    original_title = scrapy.Field()
    original_url = scrapy.Field()
    image_url = scrapy.Field()
    raw_html_content = scrapy.Field()  # Useful if Gemma needs to read the full body text later