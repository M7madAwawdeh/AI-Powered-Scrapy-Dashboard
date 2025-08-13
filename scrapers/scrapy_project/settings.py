"""
Scrapy settings for AI-Powered Scrapy Dashboard
"""

BOT_NAME = 'ai_scrapy_dashboard'

SPIDER_MODULES = ['scrapers.scrapy_project.spiders']
NEWSPIDER_MODULE = 'scrapers.scrapy_project.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': True,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': True,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': True,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': True,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': True,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'scrapers.scrapy_project.pipelines.DatabasePipeline': 300,
    'scrapers.scrapy_project.pipelines.DataCleaningPipeline': 200,
}

# Enable and configure the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/scrapy.log'

# Feed exports
FEED_FORMAT = 'json'
FEED_URI = 'exports/products_%(time)s.json'

# Custom settings
CUSTOM_SETTINGS = {
    'DOWNLOAD_TIMEOUT': 30,
    'DOWNLOAD_MAXSIZE': 10485760,  # 10MB
    'DOWNLOAD_WARNSIZE': 1048576,  # 1MB
} 