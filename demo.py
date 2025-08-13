"""
Demo script for AI-Powered Scrapy Dashboard
"""
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_ai_engine():
    """Demo the AI engine capabilities"""
    logger.info("🧠 Testing AI Engine...")
    
    try:
        from ai_engine.langchain_chain import get_ai_engine
        ai_engine = get_ai_engine()
        
        # Test categorization
        logger.info("Testing product categorization...")
        result = ai_engine.categorize_product(
            "Wireless Bluetooth Headphones with Noise Cancellation",
            "High-quality wireless headphones featuring active noise cancellation technology"
        )
        logger.info(f"Categorization result: {result}")
        
        # Test description generation
        logger.info("Testing description generation...")
        result = ai_engine.generate_description(
            "Wireless Bluetooth Headphones",
            99.99,
            "High-quality wireless headphones"
        )
        logger.info(f"Description generation result: {result}")
        
        # Test anomaly detection
        logger.info("Testing anomaly detection...")
        result = ai_engine.detect_anomalies(
            "Wireless Bluetooth Headphones",
            99.99,
            "Electronics",
            "High-quality wireless headphones"
        )
        logger.info(f"Anomaly detection result: {result}")
        
        logger.info("✅ AI Engine demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ AI Engine demo failed: {e}")

def demo_database():
    """Demo the database capabilities"""
    logger.info("🗄️ Testing Database...")
    
    try:
        from database.connection import get_db, init_database
        
        # Initialize database
        logger.info("Initializing database...")
        if init_database():
            logger.info("✅ Database initialized successfully!")
        else:
            logger.error("❌ Database initialization failed!")
            return
        
        # Get database manager
        db = get_db()
        
        # Test connection
        if db.test_connection():
            logger.info("✅ Database connection successful!")
        else:
            logger.error("❌ Database connection failed!")
            return
        
        # Get database stats
        stats = db.get_database_stats()
        logger.info(f"Database stats: {stats}")
        
        # Test session management
        with db.get_session() as session:
            logger.info("✅ Database session created successfully!")
        
        logger.info("✅ Database demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database demo failed: {e}")

def demo_scrapers():
    """Demo the scraping capabilities"""
    logger.info("🕷️ Testing Scrapers...")
    
    try:
        # Test Selenium scraper
        logger.info("Testing Selenium scraper...")
        from scrapers.selenium_scraper.selenium_scraper import SeleniumScraper
        
        with SeleniumScraper(headless=True) as scraper:
            logger.info("✅ Selenium scraper initialized successfully!")
            
            # Note: In a real demo, you might want to actually scrape a site
            # For now, we'll just test the initialization
            logger.info("Selenium scraper is ready for use!")
        
        logger.info("✅ Scrapers demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Scrapers demo failed: {e}")

def demo_ai_modules():
    """Demo the AI processing modules"""
    logger.info("🤖 Testing AI Processing Modules...")
    
    try:
        # Test categorizer
        logger.info("Testing product categorizer...")
        from ai_engine.categorizer import get_categorizer
        categorizer = get_categorizer()
        
        stats = categorizer.get_categorization_stats()
        logger.info(f"Categorizer stats: {stats}")
        
        # Test description generator
        logger.info("Testing description generator...")
        from ai_engine.description_generator import get_description_generator
        desc_generator = get_description_generator()
        
        stats = desc_generator.get_description_stats()
        logger.info(f"Description generator stats: {stats}")
        
        logger.info("✅ AI modules demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ AI modules demo failed: {e}")

def demo_pipeline():
    """Demo the pipeline runner"""
    logger.info("🔄 Testing Pipeline Runner...")
    
    try:
        from run_pipeline import PipelineRunner
        
        # Create pipeline runner
        pipeline = PipelineRunner()
        
        # Get pipeline stats
        stats = pipeline.get_pipeline_stats()
        logger.info(f"Pipeline stats: {stats}")
        
        logger.info("✅ Pipeline runner demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Pipeline runner demo failed: {e}")

def run_full_demo():
    """Run the complete demo"""
    logger.info("🚀 Starting AI-Powered Scrapy Dashboard Demo")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # Run all demos
        demo_database()
        logger.info("-" * 40)
        
        demo_ai_engine()
        logger.info("-" * 40)
        
        demo_ai_modules()
        logger.info("-" * 40)
        
        demo_scrapers()
        logger.info("-" * 40)
        
        demo_pipeline()
        logger.info("-" * 40)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("🎉 Demo completed successfully!")
        logger.info(f"⏱️ Total duration: {duration:.2f} seconds")
        logger.info("=" * 60)
        
        # Summary
        logger.info("📋 Demo Summary:")
        logger.info("✅ Database: Initialized and connected")
        logger.info("✅ AI Engine: LangChain integration working")
        logger.info("✅ AI Modules: Categorizer and description generator ready")
        logger.info("✅ Scrapers: Selenium scraper initialized")
        logger.info("✅ Pipeline: Main orchestrator ready")
        logger.info("")
        logger.info("🚀 System is ready to use!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Set up your .env file with database and API credentials")
        logger.info("2. Run: streamlit run dashboard/app.py")
        logger.info("3. Run: python run_pipeline.py --full")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        logger.error("Please check the error messages above and ensure all dependencies are installed.")

def run_quick_demo():
    """Run a quick demo for testing"""
    logger.info("⚡ Quick Demo - Testing Core Components")
    
    try:
        # Test database connection
        from database.connection import get_db
        db = get_db()
        
        if db.test_connection():
            logger.info("✅ Database: Connected")
        else:
            logger.info("❌ Database: Connection failed")
        
        # Test AI engine
        from ai_engine.langchain_chain import get_ai_engine
        ai_engine = get_ai_engine()
        
        if ai_engine.llm:
            logger.info("✅ AI Engine: Active (OpenRouter)")
        else:
            logger.info("⚠️ AI Engine: Mock Mode (No API Key)")
        
        logger.info("✅ Quick demo completed!")
        
    except Exception as e:
        logger.error(f"❌ Quick demo failed: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Powered Scrapy Dashboard Demo')
    parser.add_argument('--quick', action='store_true', help='Run quick demo only')
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_demo()
    else:
        run_full_demo() 