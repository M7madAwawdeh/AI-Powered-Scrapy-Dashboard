"""
Selenium-based scraper for JavaScript-heavy e-commerce sites
"""
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

from database.connection import get_db
from database.models import Product, Source, PriceHistory

logger = logging.getLogger(__name__)


class SeleniumScraper:
    """Selenium-based scraper for dynamic websites"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.db = get_db()
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Performance and stability options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Disable images for faster loading
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")  # We'll enable it per site if needed
            
            # Setup service
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            
            logger.info("Selenium WebDriver setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise
    
    def scrape_demo_ecommerce(self, base_url: str = "https://demo.opencart.com") -> List[Dict[str, Any]]:
        """Scrape demo OpenCart e-commerce site"""
        try:
            logger.info(f"Starting to scrape demo e-commerce site: {base_url}")
            
            # Navigate to main page
            self.driver.get(base_url)
            time.sleep(3)  # Wait for page to load
            
            products = []
            
            # Find product containers
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product-thumb")
            
            for product_element in product_elements[:10]:  # Limit to first 10 products for demo
                try:
                    product_data = self._extract_product_data(product_element, base_url)
                    if product_data:
                        products.append(product_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to extract product data: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(products)} products from demo site")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping demo e-commerce site: {e}")
            return []
    
    def _extract_product_data(self, product_element, base_url: str) -> Optional[Dict[str, Any]]:
        """Extract product data from a product element"""
        try:
            # Extract basic information
            title = product_element.find_element(By.CSS_SELECTOR, ".caption h4 a").text.strip()
            
            # Extract price
            try:
                price_element = product_element.find_element(By.CSS_SELECTOR, ".price .price-new")
                price = price_element.text.strip()
            except NoSuchElementException:
                try:
                    price_element = product_element.find_element(By.CSS_SELECTOR, ".price")
                    price = price_element.text.strip()
                except NoSuchElementException:
                    price = None
            
            # Extract image URL
            try:
                img_element = product_element.find_element(By.CSS_SELECTOR, "img")
                image_url = img_element.get_attribute("src")
                if image_url and not image_url.startswith('http'):
                    image_url = base_url + image_url
            except NoSuchElementException:
                image_url = None
            
            # Extract product URL
            try:
                link_element = product_element.find_element(By.CSS_SELECTOR, ".caption h4 a")
                product_url = link_element.get_attribute("href")
            except NoSuchElementException:
                product_url = None
            
            # Extract rating
            try:
                rating_elements = product_element.find_elements(By.CSS_SELECTOR, ".rating .fa-star")
                rating = len(rating_elements) if rating_elements else None
            except NoSuchElementException:
                rating = None
            
            # Extract availability
            try:
                availability_element = product_element.find_element(By.CSS_SELECTOR, ".availability")
                availability = availability_element.text.strip()
            except NoSuchElementException:
                availability = "In Stock"  # Default assumption
            
            # Clean price
            if price:
                price = self._clean_price(price)
            
            # Create product data
            product_data = {
                'title': title,
                'price': price,
                'currency': 'USD',
                'image_url': image_url,
                'source_url': product_url,
                'short_description': f"Product: {title}",
                'availability': availability,
                'rating': rating,
                'brand': 'Demo OpenCart',
                'model': 'Demo Product',
                'scraped_at': datetime.now()
            }
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Error extracting product data: {e}")
            return None
    
    def _clean_price(self, price_str: str) -> Optional[float]:
        """Clean and parse price string"""
        if not price_str:
            return None
        
        # Remove currency symbols and extra text
        import re
        price_match = re.search(r'[\d,]+\.?\d*', price_str)
        if price_match:
            price_str = price_match.group()
            price_str = price_str.replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    def scrape_amazon_style(self, base_url: str) -> List[Dict[str, Any]]:
        """Scrape Amazon-style e-commerce sites (template)"""
        try:
            logger.info(f"Starting to scrape Amazon-style site: {base_url}")
            
            # This is a template for Amazon-style sites
            # You would need to customize selectors for specific sites
            
            self.driver.get(base_url)
            time.sleep(5)  # Wait for dynamic content
            
            products = []
            
            # Example selectors for Amazon-style sites
            selectors = {
                'product_container': '.s-result-item',
                'title': '.a-text-normal',
                'price': '.a-price-whole',
                'image': '.s-image',
                'rating': '.a-icon-alt',
                'availability': '.a-color-success'
            }
            
            # Implementation would go here
            # This is a placeholder for the actual scraping logic
            
            logger.info("Amazon-style scraping template completed")
            return products
            
        except Exception as e:
            logger.error(f"Error in Amazon-style scraping: {e}")
            return []
    
    def save_to_database(self, products: List[Dict[str, Any]], source_name: str, base_url: str):
        """Save scraped products to database"""
        try:
            with self.db.get_session() as session:
                # Get or create source
                source = self._get_or_create_source(session, source_name, base_url)
                
                saved_count = 0
                for product_data in products:
                    try:
                        # Check if product already exists
                        existing_product = session.query(Product).filter(
                            Product.source_url == product_data['source_url'],
                            Product.source_id == source.id
                        ).first()
                        
                        if existing_product:
                            # Update existing product
                            self._update_product(existing_product, product_data)
                        else:
                            # Create new product
                            product = self._create_product(product_data, source.id)
                            session.add(product)
                        
                        saved_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to save product {product_data.get('title', 'Unknown')}: {e}")
                        continue
                
                session.commit()
                logger.info(f"Successfully saved {saved_count} products to database")
                
        except Exception as e:
            logger.error(f"Error saving products to database: {e}")
            raise
    
    def _get_or_create_source(self, session, name: str, base_url: str):
        """Get existing source or create new one"""
        source = session.query(Source).filter(Source.base_url == base_url).first()
        if not source:
            source = Source(
                name=name,
                base_url=base_url,
                site_type='selenium',
                enabled=True
            )
            session.add(source)
            session.flush()
        
        return source
    
    def _create_product(self, product_data: Dict[str, Any], source_id: int) -> Product:
        """Create new product from scraped data"""
        return Product(
            title=product_data['title'],
            price=product_data.get('price'),
            currency=product_data.get('currency', 'USD'),
            image_url=product_data.get('image_url'),
            source_url=product_data['source_url'],
            short_description=product_data.get('short_description'),
            availability=product_data.get('availability'),
            rating=product_data.get('rating'),
            source_id=source_id,
            scraped_at=product_data.get('scraped_at', datetime.now())
        )
    
    def _update_product(self, product: Product, product_data: Dict[str, Any]):
        """Update existing product with new data"""
        product.title = product_data['title']
        product.price = product_data.get('price')
        product.currency = product_data.get('currency', 'USD')
        product.image_url = product_data.get('image_url')
        product.short_description = product_data.get('short_description')
        product.availability = product_data.get('availability')
        product.rating = product_data.get('rating')
        product.scraped_at = product_data.get('scraped_at', datetime.now())
        product.updated_at = datetime.now()
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def run_selenium_scraper():
    """Run the Selenium scraper as a standalone script"""
    try:
        with SeleniumScraper(headless=True) as scraper:
            # Scrape demo e-commerce site
            products = scraper.scrape_demo_ecommerce()
            
            if products:
                # Save to database
                scraper.save_to_database(products, "Demo OpenCart", "https://demo.opencart.com")
                print(f"Successfully scraped and saved {len(products)} products")
            else:
                print("No products were scraped")
                
    except Exception as e:
        logger.error(f"Selenium scraper failed: {e}")
        print(f"Scraping failed: {e}")


if __name__ == "__main__":
    run_selenium_scraper() 