"""
Scrapy spider for books.toscrape.com
"""
import scrapy
import logging
from urllib.parse import urljoin
from datetime import datetime

from scrapers.scrapy_project.items import ProductItem

logger = logging.getLogger(__name__)


class BookSpider(scrapy.Spider):
    name = 'books_toscrape'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': False,
    }
    
    def __init__(self, *args, **kwargs):
        super(BookSpider, self).__init__(*args, **kwargs)
        self.books_scraped = 0
        self.pages_scraped = 0
    
    def parse(self, response):
        """Parse the main page and extract category links"""
        logger.info(f"Starting to parse main page: {response.url}")
        
        # Extract category links
        category_links = response.css('div.side_categories ul.nav-list li ul li a::attr(href)').getall()
        
        for category_link in category_links:
            category_url = urljoin(response.url, category_link)
            logger.info(f"Following category link: {category_url}")
            yield scrapy.Request(
                url=category_url,
                callback=self.parse_category,
                meta={'category': category_link.split('/')[-2]}
            )
    
    def parse_category(self, response):
        """Parse category page and extract book links"""
        category = response.meta.get('category', 'unknown')
        logger.info(f"Parsing category: {category} at {response.url}")
        
        # Extract book links from current page
        book_links = response.css('h3 a::attr(href)').getall()
        
        for book_link in book_links:
            book_url = urljoin(response.url, book_link)
            yield scrapy.Request(
                url=book_url,
                callback=self.parse_book,
                meta={'category': category}
            )
        
        # Check for next page
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)
            logger.info(f"Following next page: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_category,
                meta={'category': category}
            )
    
    def parse_book(self, response):
        """Parse individual book page and extract product data"""
        try:
            category = response.meta.get('category', 'unknown')
            logger.info(f"Parsing book: {response.url}")
            
            # Extract book information
            title = response.css('h1::text').get()
            price = response.css('p.price_color::text').get()
            availability = response.css('p.availability::text').get()
            rating = response.css('p.star-rating::attr(class)').get()
            image_url = response.css('div.item.active img::attr(src)').get()
            
            # Extract description
            description = response.css('div#product_description + p::text').get()
            if not description:
                description = response.css('meta[name="description"]::attr(content)').get()
            
            # Extract additional information
            upc = response.css('table.table-striped tr:contains("UPC") td::text').get()
            product_type = response.css('table.table-striped tr:contains("Product Type") td::text').get()
            price_excl_tax = response.css('table.table-striped tr:contains("Price (excl. tax)") td::text').get()
            price_incl_tax = response.css('table.table-striped tr:contains("Price (incl. tax)") td::text').get()
            tax = response.css('table.table-striped tr:contains("Tax") td::text').get()
            number_of_reviews = response.css('table.table-striped tr:contains("Number of reviews") td::text').get()
            
            # Clean and process data
            if title:
                title = title.strip()
            
            if price:
                price = price.strip().replace('£', '')
            
            if availability:
                availability = availability.strip()
            
            if rating:
                rating = rating.replace('star-rating ', '').replace('One', '1').replace('Two', '2').replace('Three', '3').replace('Four', '4').replace('Five', '5')
                try:
                    rating = float(rating)
                except ValueError:
                    rating = None
            
            if image_url:
                image_url = urljoin(response.url, image_url)
            
            if description:
                description = description.strip()
            
            # Convert review count to integer
            if number_of_reviews:
                try:
                    number_of_reviews = int(number_of_reviews.strip())
                except ValueError:
                    number_of_reviews = None
            
            # Create product item
            item = ProductItem()
            item['title'] = title
            item['price'] = price
            item['currency'] = 'GBP'
            item['image_url'] = image_url
            item['source_url'] = response.url
            item['short_description'] = description
            item['availability'] = availability
            item['rating'] = rating
            item['review_count'] = number_of_reviews
            item['external_id'] = upc
            
            # Add additional metadata
            item['brand'] = 'Books to Scrape'
            item['model'] = product_type
            item['sku'] = upc
            
            self.books_scraped += 1
            logger.info(f"Successfully scraped book {self.books_scraped}: {title[:50]}...")
            
            yield item
            
        except Exception as e:
            logger.error(f"Error parsing book {response.url}: {e}")
            # Continue with next book instead of failing completely
    
    def closed(self, reason):
        """Called when spider is closed"""
        logger.info(f"BookSpider closed. Reason: {reason}")
        logger.info(f"Total books scraped: {self.books_scraped}")
        logger.info(f"Total pages scraped: {self.pages_scraped}")


class QuoteSpider(scrapy.Spider):
    """Spider for quotes.toscrape.com (bonus spider)"""
    name = 'quotes_toscrape'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': False,
    }
    
    def parse(self, response):
        """Parse quotes page and extract quote data"""
        logger.info(f"Parsing quotes page: {response.url}")
        
        # Extract quotes from current page
        quotes = response.css('div.quote')
        
        for quote in quotes:
            text = quote.css('span.text::text').get()
            author = quote.css('small.author::text').get()
            tags = quote.css('div.tags a.tag::text').getall()
            
            if text and author:
                # Create a product-like item for quotes
                item = ProductItem()
                item['title'] = f"Quote by {author}"
                item['short_description'] = text
                item['source_url'] = response.url
                item['brand'] = 'Quotes to Scrape'
                item['model'] = 'Quote'
                item['tags'] = tags
                
                yield item
        
        # Check for next page
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse) 