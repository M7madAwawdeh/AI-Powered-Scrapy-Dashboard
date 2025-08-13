"""
Database models for AI-Powered Scrapy Dashboard
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, 
    Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class Source(Base):
    """E-commerce sites being scraped"""
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    base_url = Column(String(500), nullable=False, unique=True)
    site_type = Column(String(50), nullable=False)  # scrapy, selenium
    enabled = Column(Boolean, default=True)
    last_scraped = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="source")
    
    def __repr__(self):
        return f"<Source(name='{self.name}', url='{self.base_url}')>"


class Product(Base):
    """Scraped product data"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    external_id = Column(String(100), nullable=True)  # ID from source site
    title = Column(String(500), nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default='USD')
    image_url = Column(String(1000), nullable=True)
    source_url = Column(String(1000), nullable=False)
    short_description = Column(Text, nullable=True)
    availability = Column(String(100), nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    
    # Metadata
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    scraped_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    source = relationship("Source", back_populates="products")
    ai_enrichment = relationship("AIEnrichment", back_populates="product", uselist=False)
    price_history = relationship("PriceHistory", back_populates="product")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_product_title', 'title'),
        Index('idx_product_price', 'price'),
        Index('idx_product_scraped_at', 'scraped_at'),
        Index('idx_product_source', 'source_id'),
    )
    
    def __repr__(self):
        return f"<Product(title='{self.title[:50]}...', price={self.price})>"


class AIEnrichment(Base):
    """AI-generated content and categorization"""
    __tablename__ = 'ai_enrichment'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, unique=True)
    
    # AI Classification
    category = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=True)
    
    # AI-Generated Content
    ai_description = Column(Text, nullable=True)
    ai_title = Column(String(500), nullable=True)
    ai_tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Anomaly Detection
    anomaly_score = Column(Float, nullable=True)
    anomaly_details = Column(Text, nullable=True)
    is_flagged = Column(Boolean, default=False)
    
    # Metadata
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    generated_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="ai_enrichment")
    
    def __repr__(self):
        return f"<AIEnrichment(category='{self.category}', confidence={self.confidence_score})>"


class PriceHistory(Base):
    """Track price changes over time"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    recorded_at = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_price_history_product', 'product_id'),
        Index('idx_price_history_date', 'recorded_at'),
    )
    
    def __repr__(self):
        return f"<PriceHistory(price={self.price}, date={self.recorded_at})>"


class ScrapingSession(Base):
    """Track scraping sessions and performance"""
    __tablename__ = 'scraping_sessions'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    session_id = Column(String(100), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Session details
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default='running')  # running, completed, failed
    
    # Performance metrics
    products_scraped = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)  # seconds
    
    # Error details
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Relationships
    source = relationship("Source")
    
    def __repr__(self):
        return f"<ScrapingSession(id='{self.session_id}', status='{self.status}')>"


class AIProcessingLog(Base):
    """Log AI processing activities"""
    __tablename__ = 'ai_processing_logs'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    operation_type = Column(String(50), nullable=False)  # categorization, description, anomaly
    
    # Processing details
    model_used = Column(String(100), nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    
    # Results
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    processed_at = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("Product")
    
    def __repr__(self):
        return f"<AIProcessingLog(operation='{self.operation_type}', success={self.success})>"


# Create all tables
def create_all_tables(engine):
    """Create all database tables"""
    Base.metadata.create_all(engine)


# Drop all tables (for development/testing)
def drop_all_tables(engine):
    """Drop all database tables"""
    Base.metadata.drop_all(engine) 