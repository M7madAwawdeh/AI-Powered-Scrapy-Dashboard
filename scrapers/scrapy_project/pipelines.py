"""
Scrapy pipelines for data processing and storage
"""
import logging
import re
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal

from scrapy import signals
from scrapy.exceptions import DropItem

from database.connection import get_db
from database.models import Product, Source, PriceHistory

logger = logging.getLogger(__name__)


class DataCleaningPipeline:
    """Clean and validate scraped data"""
    
    def __init__(self):
        self.stats = {}
    
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline
    
    def spider_opened(self, spider):
        logger.info(f"DataCleaningPipeline opened for spider: {spider.name}")
    
    def spider_closed(self, spider):
        logger.info(f"DataCleaningPipeline closed for spider: {spider.name}")
        logger.info(f"Cleaning stats: {self.stats}")
    
    def process_item(self, item, spider):
        """Clean and validate item data"""
        try:
            # Clean title
            if 'title' in item and item['title']:
                item['title'] = self._clean_text(item['title'])
            
            # Clean and parse price
            if 'price' in item and item['price']:
                item['price'] = self._parse_price(item['price'])
                item['currency'] = self._extract_currency(item['price'])
            
            # Clean description
            if 'short_description' in item and item['short_description']:
                item['short_description'] = self._clean_text(item['short_description'])
            
            # Clean image URL
            if 'image_url' in item and item['image_url']:
                item['image_url'] = self._clean_url(item['image_url'], spider.start_urls[0])
            
            # Set metadata
            item['scraped_at'] = datetime.now()
            item['source_name'] = spider.name
            
            # Validate required fields
            if not item.get('title'):
                raise DropItem("Missing required field: title")
            
            if not item.get('source_url'):
                raise DropItem("Missing required field: source_url")
            
            self.stats['items_cleaned'] = self.stats.get('items_cleaned', 0) + 1
            return item
            
        except Exception as e:
            logger.error(f"Error cleaning item: {e}")
            self.stats['items_failed'] = self.stats.get('items_failed', 0) + 1
            raise DropItem(f"Data cleaning failed: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?()]', '', text)
        
        return text
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        if not price_str:
            return None
        
        # Extract numeric value
        price_match = re.search(r'[\d,]+\.?\d*', str(price_str))
        if price_match:
            price_str = price_match.group()
            # Remove commas and convert to float
            price_str = price_str.replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    def _extract_currency(self, price_str: str) -> str:
        """Extract currency from price string"""
        if not price_str:
            return 'USD'
        
        # Common currency symbols
        currency_map = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR',
            '₽': 'RUB'
        }
        
        for symbol, currency in currency_map.items():
            if symbol in str(price_str):
                return currency
        
        return 'USD'
    
    def _clean_url(self, url: str, base_url: str) -> str:
        """Clean and normalize URL"""
        if not url:
            return ""
        
        # Handle relative URLs
        if url.startswith('/'):
            # Extract base domain
            base_domain = '/'.join(base_url.split('/')[:3])
            url = base_domain + url
        elif url.startswith('./'):
            url = url[2:]
            base_domain = '/'.join(base_url.split('/')[:-1])
            url = base_domain + '/' + url
        
        return url


class DatabasePipeline:
    """Store scraped items in database"""
    
    def __init__(self):
        self.db = get_db()
        self.stats = {}
    
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline
    
    def spider_opened(self, spider):
        logger.info(f"DatabasePipeline opened for spider: {spider.name}")
    
    def spider_closed(self, spider):
        logger.info(f"DatabasePipeline closed for spider: {spider.name}")
        logger.info(f"Database stats: {self.stats}")
    
    def process_item(self, item, spider):
        """Store item in database"""
        try:
            with self.db.get_session() as session:
                # Get or create source
                source = self._get_or_create_source(session, spider.name, spider.start_urls[0])
                
                # Check if product already exists
                existing_product = session.query(Product).filter(
                    Product.source_url == item['source_url'],
                    Product.source_id == source.id
                ).first()
                
                if existing_product:
                    # Update existing product
                    self._update_product(existing_product, item)
                    self.stats['products_updated'] = self.stats.get('products_updated', 0) + 1
                else:
                    # Create new product
                    product = self._create_product(item, source.id)
                    session.add(product)
                    self.stats['products_created'] = self.stats.get('products_created', 0) + 1
                
                # Add price to history if price changed
                if item.get('price') and existing_product:
                    if existing_product.price != item['price']:
                        price_history = PriceHistory(
                            product_id=existing_product.id,
                            price=item['price'],
                            currency=item.get('currency', 'USD')
                        )
                        session.add(price_history)
                        self.stats['price_records_added'] = self.stats.get('price_records_added', 0) + 1
                
                session.commit()
                logger.info(f"Successfully processed item: {item.get('title', 'Unknown')[:50]}")
                
        except Exception as e:
            logger.error(f"Error storing item in database: {e}")
            self.stats['items_failed'] = self.stats.get('items_failed', 0) + 1
            raise DropItem(f"Database storage failed: {e}")
        
        return item
    
    def _get_or_create_source(self, session, name: str, base_url: str) -> Source:
        """Get existing source or create new one"""
        source = session.query(Source).filter(Source.base_url == base_url).first()
        if not source:
            source = Source(
                name=name,
                base_url=base_url,
                site_type='scrapy',
                enabled=True
            )
            session.add(source)
            session.flush()  # Get the ID
        
        return source
    
    def _create_product(self, item: Dict[str, Any], source_id: int) -> Product:
        """Create new product from item"""
        return Product(
            title=item['title'],
            price=item.get('price'),
            currency=item.get('currency', 'USD'),
            image_url=item.get('image_url'),
            source_url=item['source_url'],
            short_description=item.get('short_description'),
            availability=item.get('availability'),
            rating=item.get('rating'),
            review_count=item.get('review_count'),
            source_id=source_id,
            scraped_at=item.get('scraped_at', datetime.now())
        )
    
    def _update_product(self, product: Product, item: Dict[str, Any]):
        """Update existing product with new data"""
        product.title = item['title']
        product.price = item.get('price')
        product.currency = item.get('currency', 'USD')
        product.image_url = item.get('image_url')
        product.short_description = item.get('short_description')
        product.availability = item.get('availability')
        product.rating = item.get('rating')
        product.review_count = item.get('review_count')
        product.scraped_at = item.get('scraped_at', datetime.now())
        product.updated_at = datetime.now() 