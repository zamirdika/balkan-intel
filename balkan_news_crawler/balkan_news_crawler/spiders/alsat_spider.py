import scrapy
from bs4 import BeautifulSoup

class AlsatSpider(scrapy.Spider):
    name = "alsat"
    allowed_domains = ["alsat.mk"]
    # We use the RSS feed because it is perfectly structured and updates instantly
    start_urls = ["https://alsat.mk/feed/"]

    def parse(self, response):
        # Scrapy can parse XML/RSS natively using the remove_namespaces trick
        response.selector.remove_namespaces()
        
        # Grab the top 5 most recent articles from the RSS feed
        items = response.xpath('//item')[:5]
        
        for item in items:
            title = item.xpath('title/text()').get()
            link = item.xpath('link/text()').get()
            
            # Follow the link to scrape the actual paragraph text
            if link:
                yield scrapy.Request(
                    url=link, 
                    callback=self.parse_article,
                    meta={'original_title': title}
                )

    def parse_article(self, response):
        # Extract paragraph text. Alsat usually puts their text inside <p> tags in the main entry-content div
        paragraphs = response.css('.entry-content p::text, .entry-content p *::text').getall()
        full_text = " ".join([p.strip() for p in paragraphs if p.strip()])
        
        # If the specific CSS fails, use BeautifulSoup as a fallback to strip all text from the main body
        if len(full_text) < 100:
            soup = BeautifulSoup(response.text, 'html.parser')
            article_body = soup.find('div', class_='entry-content')
            if article_body:
                full_text = article_body.get_text(separator=' ', strip=True)

        yield {
            'source_domain': 'Alsat-M',
            'original_title': response.meta['original_title'],
            'original_url': response.url,
            'image_url': response.css('meta[property="og:image"]::attr(content)').get(),
            'raw_html_content': full_text
        }