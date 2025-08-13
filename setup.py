"""
Setup script for AI-Powered Scrapy Dashboard
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ is required. Current version: %s", sys.version)
        return False
    logger.info("✅ Python version check passed: %s", sys.version)
    return True

def install_requirements():
    """Install required packages"""
    try:
        logger.info("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("❌ Failed to install requirements: %s", e)
        return False

def create_env_file():
    """Create .env file template"""
    env_content = """# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_scrapy_dashboard
DB_USER=postgres
DB_PASSWORD=your_password_here

# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Scraping Configuration
SCRAPING_DELAY=2
SCRAPING_TIMEOUT=30
SCRAPING_RETRY_TIMES=3

# Dashboard Configuration
DASHBOARD_PORT=8501
DASHBOARD_HOST=localhost

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/scrapy_dashboard.log

# Development Settings
DEBUG=True
ENVIRONMENT=development
"""
    
    if not os.path.exists('.env'):
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            logger.info("✅ Created .env file template")
            logger.info("⚠️ Please edit .env file with your actual credentials")
            return True
        except Exception as e:
            logger.error("❌ Failed to create .env file: %s", e)
            return False
    else:
        logger.info("✅ .env file already exists")
        return True

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'exports', 'httpcache']
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info("✅ Created directory: %s", directory)
            except Exception as e:
                logger.error("❌ Failed to create directory %s: %s", directory, e)
                return False
    
    return True

def check_dependencies():
    """Check if key dependencies are available"""
    try:
        import scrapy
        logger.info("✅ Scrapy: %s", scrapy.__version__)
    except ImportError:
        logger.error("❌ Scrapy not found")
        return False
    
    try:
        import streamlit
        logger.info("✅ Streamlit: %s", streamlit.__version__)
    except ImportError:
        logger.error("❌ Streamlit not found")
        return False
    
    try:
        import sqlalchemy
        logger.info("✅ SQLAlchemy: %s", sqlalchemy.__version__)
    except ImportError:
        logger.error("❌ SQLAlchemy not found")
        return False
    
    try:
        import langchain
        logger.info("✅ LangChain: %s", langchain.__version__)
    except ImportError:
        logger.error("❌ LangChain not found")
        return False
    
    return True

def run_demo():
    """Run a quick demo to test the setup"""
    try:
        logger.info("Running quick demo...")
        subprocess.check_call([sys.executable, "demo.py", "--quick"])
        return True
    except subprocess.CalledProcessError as e:
        logger.error("❌ Demo failed: %s", e)
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Setting up AI-Powered Scrapy Dashboard")
    logger.info("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Run demo
    logger.info("Testing setup with demo...")
    if run_demo():
        logger.info("✅ Setup completed successfully!")
        logger.info("")
        logger.info("🎉 Your AI-Powered Scrapy Dashboard is ready!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Edit .env file with your database and API credentials")
        logger.info("2. Start the dashboard: streamlit run dashboard/app.py")
        logger.info("3. Run the pipeline: python run_pipeline.py --full")
        logger.info("")
        logger.info("📚 For more information, see README.md")
        return True
    else:
        logger.error("❌ Setup completed but demo failed")
        logger.info("Please check the error messages above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 