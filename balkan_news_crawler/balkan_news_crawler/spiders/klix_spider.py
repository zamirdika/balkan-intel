import scrapy
from balkan_news_crawler.items import BalkanNewsCrawlerItem

class KlixSpider(scrapy.Spider):
    # The unique name Scrapy uses to run this specific spider
    name = "klix"
    
    # Prevents the spider from wandering off to external sites like Facebook or Google
    allowed_domains = ["klix.ba"]
    
    # The entry point where the spider begins its journey
    start_urls = ["https://www.klix.ba/rss"]

    def parse(self, response):
        """
        This method parses the RSS XML feed to find individual article links.
        """
        # Scrapy can read XML/RSS using selectors. We pull all <item> tags.
        articles = response.xpath("//item")
        
        for article in articles[:5]: # Limit to 5 articles during our testing phase
            item = BalkanNewsCrawlerItem()
            
            # Extract basic data points from the RSS item
            item['source_domain'] = "Klix"
            item['original_title'] = article.xpath("title/text()").get()
            item['original_url'] = article.xpath("link/text()").get()
            
            # Crucial Part: Instead of guessing the image URL from the RSS,
            # we tell Scrapy to follow the article link to read the actual web page!
            article_url = item['original_url']
            if article_url:
                yield scrapy.Request(
                    url=article_url, 
                    callback=self.parse_article_page, 
                    meta={'item': item}
                )

    def parse_article_page(self, response):
        item = response.meta['item']
        
        self.logger.info(f"Inspecting live page HTML for: {response.url}")
        
        # Extract the pristine OpenGraph image
        meta_image = response.css('meta[property="og:image"]::attr(content)').get()
        if meta_image:
            item['image_url'] = meta_image
        else:
            item['image_url'] = response.css('article img::attr(src)').get() or ""
            
        # 🚀 NEW: Extract the full article text for the local AI core
        # We grab all text inside paragraphs within the main article container
        paragraphs = response.css('article p::text, .article-body p::text').getall()
        # Clean and join the paragraphs into a single continuous block of text
        full_text = " ".join([p.strip() for p in paragraphs if p.strip()])
        
        item['raw_html_content'] = full_text
        
        yield item