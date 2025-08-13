"""
Scrapy items for product data
"""
import scrapy
from scrapy import Field


class ProductItem(scrapy.Item):
    """Item for scraped product data"""
    
    # Basic product information
    title = Field()
    price = Field()
    currency = Field()
    image_url = Field()
    source_url = Field()
    short_description = Field()
    availability = Field()
    rating = Field()
    review_count = Field()
    
    # Metadata
    external_id = Field()
    source_name = Field()
    scraped_at = Field()
    
    # Additional fields that might be available
    brand = Field()
    model = Field()
    sku = Field()
    condition = Field()
    shipping_info = Field()
    
    def __repr__(self):
        return f"<ProductItem(title='{self.get('title', 'N/A')[:50]}...', price={self.get('price', 'N/A')})>"


class QuoteItem(scrapy.Item):
    """Item for scraped quote data (for quotes.toscrape.com)"""
    
    text = Field()
    author = Field()
    tags = Field()
    source_url = Field()
    scraped_at = Field()
    
    def __repr__(self):
        return f"<QuoteItem(author='{self.get('author', 'N/A')}', text='{self.get('text', 'N/A')[:50]}...')>" 