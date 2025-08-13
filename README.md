# 🕷️ AI-Powered Scrapy Dashboard

A comprehensive, intelligent data collection and analysis system that combines web scraping with AI-powered insights. This project demonstrates mastery of web scraping, data pipelines, AI-powered NLP, and full-cycle data intelligence.

## 🌟 Features

### 🔍 **Multi-Source Web Scraping**
- **Scrapy Integration**: Robust spiders for static websites (books.toscrape.com, quotes.toscrape.com)
- **Selenium Support**: JavaScript-heavy site scraping with browser automation
- **Smart Data Extraction**: Product titles, prices, images, descriptions, ratings, availability
- **Responsible Scraping**: Configurable delays, user agents, and retry mechanisms

### 🧠 **AI-Powered Intelligence**
- **Product Categorization**: Zero-shot classification using LangChain + OpenRouter
- **Enhanced Descriptions**: AI-generated, SEO-friendly product descriptions
- **Anomaly Detection**: Price analysis and data quality assessment
- **Smart Tagging**: Automatic keyword extraction and categorization

### 📊 **Interactive Dashboard**
- **Real-time Monitoring**: Live product feed and scraping status
- **Advanced Analytics**: Price trends, category distribution, source performance
- **AI Insights**: Side-by-side comparison of original vs AI-enhanced content
- **Data Management**: Filtering, searching, and export capabilities

### 🗄️ **Robust Data Pipeline**
- **PostgreSQL Storage**: Normalized schema with proper indexing
- **Data Validation**: Cleaning, parsing, and quality checks
- **Price History Tracking**: Temporal analysis and trend detection
- **Comprehensive Logging**: AI processing, scraping sessions, and errors

## 🏗️ Architecture

```
ai_powered_scrapy/
├── scrapers/                 # Web scraping engines
│   ├── scrapy_project/      # Scrapy spiders and pipelines
│   └── selenium_scraper/    # Browser automation scraper
├── ai_engine/               # AI processing modules
│   ├── langchain_chain.py   # LangChain integration
│   ├── categorizer.py       # Product categorization
│   └── description_generator.py # Description generation
├── database/                # Data persistence layer
│   ├── models.py           # SQLAlchemy ORM models
│   └── connection.py       # Database management
├── dashboard/               # Streamlit web interface
│   └── app.py              # Main dashboard application
├── config/                  # Configuration management
│   └── settings.py         # Settings and constants
├── run_pipeline.py          # Main pipeline orchestrator
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start

### 1. **Prerequisites**
- Python 3.8+
- PostgreSQL 12+
- Chrome/Chromium (for Selenium)

### 2. **Installation**

```bash
# Clone the repository
git clone <repository-url>
cd ai_powered_scrapy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. **Environment Setup**

Create a `.env` file in the project root:

```bash
# Database Configuration
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
```

### 4. **Database Setup**

```bash
# Create PostgreSQL database
createdb ai_scrapy_dashboard

# Initialize database tables
python -c "from database.connection import init_database; init_database()"
```

### 5. **Run the System**

```bash
# Start the dashboard
streamlit run dashboard/app.py

# Run the full pipeline
python run_pipeline.py --full

# Run specific phases
python run_pipeline.py --scrape --categorize
```

## 📖 Usage Examples

### **Running Scrapers**

```python
# Run Scrapy spider for books
from scrapers.scrapy_project.spiders.book_spider import BookSpider
# Use Scrapy CLI: scrapy crawl books_toscrape

# Run Selenium scraper
from scrapers.selenium_scraper.selenium_scraper import SeleniumScraper
with SeleniumScraper() as scraper:
    products = scraper.scrape_demo_ecommerce()
```

### **AI Processing**

```python
# Categorize products
from ai_engine.categorizer import get_categorizer
categorizer = get_categorizer()
result = categorizer.categorize_products(limit=100)

# Generate descriptions
from ai_engine.description_generator import get_description_generator
generator = get_description_generator()
result = generator.generate_descriptions(limit=50)
```

### **Database Operations**

```python
from database.connection import get_db
db = get_db()

# Get database stats
stats = db.get_database_stats()

# Query products
with db.get_session() as session:
    products = session.query(Product).limit(10).all()
```

## 🔧 Configuration

### **Target Sites**

Configure scraping targets in `config/settings.py`:

```python
TARGET_SITES = {
    'books_toscrape': {
        'name': 'Books to Scrape',
        'base_url': 'http://books.toscrape.com',
        'type': 'scrapy',
        'enabled': True,
    },
    'demo_ecommerce': {
        'name': 'Demo E-commerce',
        'base_url': 'https://demo.opencart.com',
        'type': 'selenium',
        'enabled': False,
    }
}
```

### **AI Models**

Configure AI providers and models:

```python
OPENROUTER_CONFIG = {
    'api_key': os.getenv('OPENROUTER_API_KEY'),
    'model': 'anthropic/claude-3.5-sonnet',
    'max_tokens': 1000,
    'temperature': 0.7,
}
```

### **Scraping Settings**

```python
SCRAPING_CONFIG = {
    'delay': 2,  # seconds between requests
    'user_agent': 'Custom Browser Agent',
    'timeout': 30,
    'retry_times': 3,
}
```

## 📊 Dashboard Features

### **Overview Tab**
- System status and database connection
- Key metrics and recent activity
- Real-time scraping statistics

### **Products Tab**
- Product management and filtering
- Search and category filtering
- Detailed product information
- AI enrichment status

### **AI Insights Tab**
- AI engine status and configuration
- Processing statistics and performance
- Category distribution charts
- Manual AI processing triggers

### **Scraping Tab**
- Source site management
- Scraping status and history
- Manual scraping controls
- Configuration settings

### **Analytics Tab**
- Price trend analysis
- Category performance metrics
- Source comparison charts
- Data export capabilities

### **Settings Tab**
- Database configuration
- AI model settings
- System maintenance tools
- Connection testing

## 🔄 Pipeline Workflow

1. **Data Collection**
   - Scrapy spiders crawl static sites
   - Selenium handles dynamic content
   - Data cleaning and validation

2. **AI Enrichment**
   - Product categorization
   - Description generation
   - Anomaly detection

3. **Data Storage**
   - PostgreSQL with proper indexing
   - Price history tracking
   - Processing logs

4. **Visualization**
   - Interactive Streamlit dashboard
   - Real-time charts and metrics
   - Export and reporting tools

## 🛠️ Development

### **Adding New Scrapers**

1. **Scrapy Spider**:
```python
# scrapers/scrapy_project/spiders/new_spider.py
class NewSpider(scrapy.Spider):
    name = 'new_site'
    allowed_domains = ['newsite.com']
    start_urls = ['https://newsite.com']
    
    def parse(self, response):
        # Implement parsing logic
        pass
```

2. **Selenium Scraper**:
```python
# scrapers/selenium_scraper/new_scraper.py
class NewSeleniumScraper(SeleniumScraper):
    def scrape_new_site(self, base_url):
        # Implement scraping logic
        pass
```

### **Custom AI Models**

```python
# ai_engine/custom_chain.py
from .langchain_chain import LangChainEngine

class CustomAIEngine(LangChainEngine):
    def custom_analysis(self, product_data):
        # Implement custom AI logic
        pass
```

## 📈 Performance & Scaling

### **Database Optimization**
- Connection pooling
- Proper indexing
- Regular cleanup of old data
- Partitioned tables for large datasets

### **Scraping Efficiency**
- Concurrent request management
- Intelligent delays and rate limiting
- Caching and deduplication
- Distributed scraping support

### **AI Processing**
- Batch processing
- Model caching
- Fallback mechanisms
- Progress tracking

## 🔒 Security & Best Practices

### **Data Protection**
- Environment variable configuration
- Database connection security
- API key management
- Input validation and sanitization

### **Responsible Scraping**
- Respect robots.txt
- Reasonable request rates
- User agent identification
- Error handling and logging

### **AI Safety**
- Content filtering
- Rate limiting
- Fallback mechanisms
- Processing validation

## 🧪 Testing

### **Unit Tests**
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/
```

### **Integration Tests**
```bash
# Test database connection
python -c "from database.connection import test_connection; test_connection()"

# Test AI engine
python -c "from ai_engine.langchain_chain import get_ai_engine; engine = get_ai_engine()"
```

## 🚀 Deployment

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py"]
```

### **Production Considerations**
- Environment-specific configurations
- Database connection pooling
- Logging and monitoring
- Backup and recovery procedures
- Load balancing for high traffic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Scrapy**: Web scraping framework
- **LangChain**: AI application framework
- **OpenRouter**: AI model access
- **Streamlit**: Dashboard framework
- **PostgreSQL**: Database system

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the documentation
- Review the code examples

---

**Built with ❤️ for intelligent data collection and analysis** 