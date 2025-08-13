"""
Database connection and session management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from typing import Optional, Generator
import time

from .models import Base, Source, Product, AIEnrichment, PriceHistory, ScrapingSession, AIProcessingLog
from config.settings import DATABASE_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            # Build connection string
            connection_string = (
                f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
                f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
            )
            
            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # Set to True for SQL debugging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def initialize_sources(self):
        """Initialize default source sites"""
        from config.settings import TARGET_SITES
        
        try:
            with self.get_session() as session:
                # Check if sources already exist
                existing_sources = session.query(Source).count()
                if existing_sources > 0:
                    logger.info("Sources already initialized, skipping...")
                    return
                
                # Create default sources
                for site_key, site_config in TARGET_SITES.items():
                    source = Source(
                        name=site_config['name'],
                        base_url=site_config['base_url'],
                        site_type=site_config['type'],
                        enabled=site_config['enabled']
                    )
                    session.add(source)
                
                session.commit()
                logger.info("Default sources initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize sources: {e}")
            raise
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        try:
            with self.get_session() as session:
                stats = {
                    'total_products': session.query(Product).count(),
                    'total_sources': session.query(Source).count(),
                    'enabled_sources': session.query(Source).filter(Source.enabled == True).count(),
                    'products_with_ai': session.query(Product).join(AIEnrichment).count(),
                    'total_categories': session.query(AIEnrichment.category).distinct().count(),
                    'recent_scrapes': session.query(Product).filter(
                        Product.scraped_at >= text("NOW() - INTERVAL '24 hours'")
                    ).count()
                }
                return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to prevent database bloat"""
        try:
            with self.get_session() as session:
                # Clean up old price history
                cutoff_date = text(f"NOW() - INTERVAL '{days_to_keep} days'")
                old_price_records = session.query(PriceHistory).filter(
                    PriceHistory.recorded_at < cutoff_date
                ).delete()
                
                # Clean up old AI processing logs
                old_ai_logs = session.query(AIProcessingLog).filter(
                    AIProcessingLog.processed_at < cutoff_date
                ).delete()
                
                # Clean up old scraping sessions
                old_sessions = session.query(ScrapingSession).filter(
                    ScrapingSession.started_at < cutoff_date
                ).delete()
                
                session.commit()
                logger.info(f"Cleaned up {old_price_records} price records, {old_ai_logs} AI logs, {old_sessions} sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    def get_connection_info(self) -> dict:
        """Get database connection information"""
        return {
            'host': DATABASE_CONFIG['host'],
            'port': DATABASE_CONFIG['port'],
            'database': DATABASE_CONFIG['database'],
            'user': DATABASE_CONFIG['user'],
            'connected': self.test_connection(),
            'pool_size': self.engine.pool.size() if self.engine else None,
            'checked_out': self.engine.pool.checkedout() if self.engine else None
        }


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> DatabaseManager:
    """Get database manager instance"""
    return db_manager


def init_database():
    """Initialize database with tables and default data"""
    try:
        # Test connection
        if not db_manager.test_connection():
            raise Exception("Database connection failed")
        
        # Create tables
        db_manager.create_tables()
        
        # Initialize default sources
        db_manager.initialize_sources()
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    # Test database connection
    if init_database():
        print("Database setup completed successfully!")
        
        # Print database stats
        stats = db_manager.get_database_stats()
        print(f"Database stats: {stats}")
    else:
        print("Database setup failed!") 