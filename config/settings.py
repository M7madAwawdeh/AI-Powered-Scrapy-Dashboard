"""
Configuration settings for AI-Powered Scrapy Dashboard
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ai_scrapy_dashboard'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
}

# OpenRouter API Configuration
OPENROUTER_CONFIG = {
    'api_key': os.getenv('OPENROUTER_API_KEY'),
    'base_url': 'https://openrouter.ai/api/v1',
    'model': os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet'),
    'max_tokens': 1000,
    'temperature': 0.7,
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'delay': 2,  # seconds between requests
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'timeout': 30,
    'retry_times': 3,
}

# Target E-commerce Sites
TARGET_SITES = {
    'books_toscrape': {
        'name': 'Books to Scrape',
        'base_url': 'http://books.toscrape.com',
        'type': 'scrapy',
        'enabled': True,
    },
    'quotes_toscrape': {
        'name': 'Quotes to Scrape',
        'base_url': 'http://quotes.toscrape.com',
        'type': 'scrapy',
        'enabled': True,
    },
    'demo_ecommerce': {
        'name': 'Demo E-commerce',
        'base_url': 'https://demo.opencart.com',
        'type': 'selenium',
        'enabled': False,  # Disabled for demo
    }
}

# Product Categories for AI Classification
PRODUCT_CATEGORIES = [
    'Books',
    'Electronics',
    'Clothing',
    'Home & Garden',
    'Sports & Outdoors',
    'Toys & Games',
    'Health & Beauty',
    'Automotive',
    'Tools & Hardware',
    'Other'
]

# AI Prompt Templates
AI_PROMPTS = {
    'categorization': """
    You are a product categorization expert. Given a product title and description, 
    classify it into one of these categories: {categories}
    
    Product Title: {title}
    Product Description: {description}
    
    Respond with only the category name from the list above.
    """,
    
    'description_generation': """
    Write a compelling, SEO-friendly product description for the following product:
    
    Title: {title}
    Price: {price}
    Original Description: {description}
    
    Requirements:
    - 100-150 words
    - Highlight key features and benefits
    - Use engaging, persuasive language
    - Include relevant keywords naturally
    - Focus on customer value proposition
    
    Enhanced Description:
    """,
    
    'anomaly_detection': """
    Analyze this product listing for potential anomalies:
    
    Title: {title}
    Price: {price}
    Category: {category}
    Description: {description}
    
    Check for:
    1. Unusually low/high pricing
    2. Misleading information
    3. Potential duplicates
    4. Quality concerns
    
    Provide a brief analysis and risk score (1-10).
    """
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'title': 'AI-Powered Scrapy Dashboard',
    'page_icon': '🕷️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/scrapy_dashboard.log',
}

# Scheduling Configuration
SCHEDULER_CONFIG = {
    'scraping_interval': 'daily',  # daily, hourly, weekly
    'scraping_time': '02:00',  # 2 AM
    'enrichment_delay': 300,  # 5 minutes after scraping
}

# Rate Limiting
RATE_LIMITS = {
    'openrouter_requests_per_minute': 60,
    'scraping_requests_per_minute': 30,
    'database_operations_per_second': 100,
} 