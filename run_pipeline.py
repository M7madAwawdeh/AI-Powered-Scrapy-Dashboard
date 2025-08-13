"""
Main pipeline runner for AI-Powered Scrapy Dashboard
"""
import logging
import time
import argparse
from datetime import datetime
from typing import Dict, Any, List

# Import our modules
from database.connection import get_db, init_database
from ai_engine.categorizer import get_categorizer
from ai_engine.description_generator import get_description_generator
from scrapers.selenium_scraper.selenium_scraper import SeleniumScraper
from config.settings import TARGET_SITES, SCHEDULER_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PipelineRunner:
    """Main pipeline orchestrator for the AI-Powered Scrapy Dashboard"""
    
    def __init__(self):
        self.db = get_db()
        self.categorizer = get_categorizer()
        self.desc_generator = get_description_generator()
        self.stats = {
            'start_time': None,
            'end_time': None,
            'products_scraped': 0,
            'products_categorized': 0,
            'descriptions_generated': 0,
            'errors': 0
        }
    
    def run_full_pipeline(self, scrape: bool = True, categorize: bool = True, 
                         generate_descriptions: bool = True) -> Dict[str, Any]:
        """Run the complete pipeline"""
        self.stats['start_time'] = datetime.now()
        logger.info("Starting full pipeline execution")
        
        try:
            # Step 1: Scraping
            if scrape:
                logger.info("Step 1: Running scraping phase")
                scraping_result = self._run_scraping_phase()
                self.stats['products_scraped'] = scraping_result.get('products_scraped', 0)
                logger.info(f"Scraping completed: {self.stats['products_scraped']} products")
            
            # Step 2: AI Categorization
            if categorize:
                logger.info("Step 2: Running AI categorization phase")
                categorization_result = self._run_categorization_phase()
                self.stats['products_categorized'] = categorization_result.get('products_successful', 0)
                logger.info(f"Categorization completed: {self.stats['products_categorized']} products")
            
            # Step 3: AI Description Generation
            if generate_descriptions:
                logger.info("Step 3: Running AI description generation phase")
                description_result = self._run_description_generation_phase()
                self.stats['descriptions_generated'] = description_result.get('products_successful', 0)
                logger.info(f"Description generation completed: {self.stats['descriptions_generated']} products")
            
            # Pipeline completed successfully
            self.stats['end_time'] = datetime.now()
            processing_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            logger.info(f"Pipeline completed successfully in {processing_time:.2f} seconds")
            
            return {
                'status': 'success',
                'message': 'Pipeline completed successfully',
                'stats': self.stats,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.stats['end_time'] = datetime.now()
            self.stats['errors'] += 1
            processing_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            logger.error(f"Pipeline failed after {processing_time:.2f} seconds: {e}")
            
            return {
                'status': 'error',
                'message': str(e),
                'stats': self.stats,
                'processing_time': processing_time
            }
    
    def _run_scraping_phase(self) -> Dict[str, Any]:
        """Run the scraping phase using both Scrapy and Selenium"""
        logger.info("Starting scraping phase")
        
        total_products = 0
        scraping_results = {}
        
        try:
            # Run Scrapy spiders for enabled sites
            for site_key, site_config in TARGET_SITES.items():
                if site_config['enabled'] and site_config['type'] == 'scrapy':
                    logger.info(f"Running Scrapy spider for {site_config['name']}")
                    
                    # In a real implementation, this would run the Scrapy spider
                    # For now, we'll simulate the process
                    result = self._run_scrapy_spider(site_key, site_config)
                    scraping_results[site_key] = result
                    total_products += result.get('products_scraped', 0)
            
            # Run Selenium scraper for enabled sites
            for site_key, site_config in TARGET_SITES.items():
                if site_config['enabled'] and site_config['type'] == 'selenium':
                    logger.info(f"Running Selenium scraper for {site_config['name']}")
                    
                    result = self._run_selenium_scraper(site_key, site_config)
                    scraping_results[site_key] = result
                    total_products += result.get('products_scraped', 0)
            
            logger.info(f"Scraping phase completed: {total_products} total products")
            
            return {
                'status': 'success',
                'products_scraped': total_products,
                'site_results': scraping_results
            }
            
        except Exception as e:
            logger.error(f"Scraping phase failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'products_scraped': total_products
            }
    
    def _run_scrapy_spider(self, site_key: str, site_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a Scrapy spider for a specific site"""
        try:
            logger.info(f"Running Scrapy spider for {site_config['name']}")
            
            # In a real implementation, this would use subprocess to run Scrapy
            # For now, we'll simulate the process
            
            # Simulate scraping delay
            time.sleep(2)
            
            # Simulate finding products
            products_found = 10  # Mock number
            
            logger.info(f"Scrapy spider for {site_config['name']} completed: {products_found} products")
            
            return {
                'status': 'success',
                'products_scraped': products_found,
                'site': site_config['name']
            }
            
        except Exception as e:
            logger.error(f"Scrapy spider for {site_key} failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'products_scraped': 0,
                'site': site_config['name']
            }
    
    def _run_selenium_scraper(self, site_key: str, site_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run Selenium scraper for a specific site"""
        try:
            logger.info(f"Running Selenium scraper for {site_config['name']}")
            
            # Use our Selenium scraper
            with SeleniumScraper(headless=True) as scraper:
                if site_key == 'demo_ecommerce':
                    products = scraper.scrape_demo_ecommerce(site_config['base_url'])
                else:
                    # For other sites, use the generic method
                    products = scraper.scrape_amazon_style(site_config['base_url'])
                
                if products:
                    # Save to database
                    scraper.save_to_database(products, site_config['name'], site_config['base_url'])
                    products_found = len(products)
                else:
                    products_found = 0
                
                logger.info(f"Selenium scraper for {site_config['name']} completed: {products_found} products")
                
                return {
                    'status': 'success',
                    'products_scraped': products_found,
                    'site': site_config['name']
                }
                
        except Exception as e:
            logger.error(f"Selenium scraper for {site_key} failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'products_scraped': 0,
                'site': site_config['name']
            }
    
    def _run_categorization_phase(self) -> Dict[str, Any]:
        """Run the AI categorization phase"""
        logger.info("Starting AI categorization phase")
        
        try:
            # Get products that need categorization
            result = self.categorizer.categorize_products(limit=100)
            
            if result['status'] == 'success':
                logger.info(f"AI categorization completed: {result['products_successful']} products processed")
                return result
            else:
                logger.error(f"AI categorization failed: {result.get('message', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"AI categorization phase failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'products_processed': 0,
                'products_successful': 0,
                'products_failed': 0
            }
    
    def _run_description_generation_phase(self) -> Dict[str, Any]:
        """Run the AI description generation phase"""
        logger.info("Starting AI description generation phase")
        
        try:
            # Get products that need description generation
            result = self.desc_generator.generate_descriptions(limit=100)
            
            if result['status'] == 'success':
                logger.info(f"AI description generation completed: {result['products_successful']} products processed")
                return result
            else:
                logger.error(f"AI description generation failed: {result.get('message', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"AI description generation phase failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'products_processed': 0,
                'products_successful': 0,
                'products_failed': 0
            }
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get current pipeline statistics"""
        return {
            'stats': self.stats,
            'database_stats': self.db.get_database_stats() if self.db else {},
            'ai_stats': {
                'categorization': self.categorizer.get_categorization_stats() if self.categorizer else {},
                'description_generation': self.desc_generator.get_description_stats() if self.desc_generator else {}
            }
        }
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to prevent database bloat"""
        try:
            logger.info(f"Cleaning up data older than {days_to_keep} days")
            self.db.cleanup_old_data(days_to_keep)
            logger.info("Data cleanup completed successfully")
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")


def main():
    """Main entry point for the pipeline"""
    parser = argparse.ArgumentParser(description='AI-Powered Scrapy Dashboard Pipeline')
    parser.add_argument('--scrape', action='store_true', help='Run scraping phase')
    parser.add_argument('--categorize', action='store_true', help='Run AI categorization phase')
    parser.add_argument('--descriptions', action='store_true', help='Run AI description generation phase')
    parser.add_argument('--full', action='store_true', help='Run full pipeline (all phases)')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old data')
    parser.add_argument('--stats', action='store_true', help='Show pipeline statistics')
    
    args = parser.parse_args()
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        if not init_database():
            logger.error("Database initialization failed!")
            return
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    
    # Create pipeline runner
    pipeline = PipelineRunner()
    
    try:
        if args.cleanup:
            # Clean up old data
            pipeline.cleanup_old_data()
            logger.info("Data cleanup completed")
            
        elif args.stats:
            # Show statistics
            stats = pipeline.get_pipeline_stats()
            logger.info("Pipeline Statistics:")
            logger.info(f"Database Stats: {stats['database_stats']}")
            logger.info(f"AI Stats: {stats['ai_stats']}")
            
        elif args.full or (not args.scrape and not args.categorize and not args.descriptions):
            # Run full pipeline
            logger.info("Running full pipeline...")
            result = pipeline.run_full_pipeline()
            
            if result['status'] == 'success':
                logger.info("Pipeline completed successfully!")
                logger.info(f"Stats: {result['stats']}")
                logger.info(f"Processing time: {result['processing_time']:.2f} seconds")
            else:
                logger.error(f"Pipeline failed: {result['message']}")
                
        else:
            # Run specific phases
            result = pipeline.run_full_pipeline(
                scrape=args.scrape,
                categorize=args.categorize,
                generate_descriptions=args.descriptions
            )
            
            if result['status'] == 'success':
                logger.info("Selected phases completed successfully!")
                logger.info(f"Stats: {result['stats']}")
            else:
                logger.error(f"Selected phases failed: {result['message']}")
                
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")


if __name__ == "__main__":
    main() 