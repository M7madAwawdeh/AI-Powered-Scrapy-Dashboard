"""
AI-powered product categorization module
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from database.connection import get_db
from database.models import Product, AIEnrichment, AIProcessingLog
from .langchain_chain import get_ai_engine

logger = logging.getLogger(__name__)


class ProductCategorizer:
    """AI-powered product categorization system"""
    
    def __init__(self):
        self.db = get_db()
        self.ai_engine = get_ai_engine()
    
    def categorize_products(self, limit: int = 100, force_reprocess: bool = False) -> Dict[str, Any]:
        """Categorize multiple products using AI"""
        start_time = datetime.now()
        
        try:
            with self.db.get_session() as session:
                # Get products that need categorization
                if force_reprocess:
                    # Get all products
                    products = session.query(Product).limit(limit).all()
                else:
                    # Get products without AI enrichment
                    products = session.query(Product).outerjoin(AIEnrichment).filter(
                        AIEnrichment.id.is_(None)
                    ).limit(limit).all()
                
                if not products:
                    logger.info("No products found for categorization")
                    return {
                        'status': 'success',
                        'message': 'No products found for categorization',
                        'products_processed': 0,
                        'processing_time': (datetime.now() - start_time).total_seconds()
                    }
                
                logger.info(f"Starting categorization of {len(products)} products")
                
                processed_count = 0
                success_count = 0
                error_count = 0
                
                for product in products:
                    try:
                        result = self._categorize_single_product(session, product)
                        if result:
                            success_count += 1
                        processed_count += 1
                        
                        # Log progress
                        if processed_count % 10 == 0:
                            logger.info(f"Processed {processed_count}/{len(products)} products")
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Failed to categorize product {product.id}: {e}")
                        continue
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                logger.info(f"Categorization completed: {success_count} success, {error_count} errors, {processing_time:.2f}s")
                
                return {
                    'status': 'success',
                    'products_processed': processed_count,
                    'products_successful': success_count,
                    'products_failed': error_count,
                    'processing_time': processing_time
                }
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Categorization process failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'products_processed': 0,
                'products_successful': 0,
                'products_failed': 0,
                'processing_time': processing_time
            }
    
    def _categorize_single_product(self, session, product: Product) -> bool:
        """Categorize a single product"""
        try:
            # Prepare product data for AI analysis
            title = product.title or ""
            description = product.short_description or ""
            
            # Get AI categorization
            ai_result = self.ai_engine.categorize_product(title, description)
            
            if not ai_result:
                logger.warning(f"No AI result for product {product.id}")
                return False
            
            # Create or update AI enrichment record
            ai_enrichment = session.query(AIEnrichment).filter(
                AIEnrichment.product_id == product.id
            ).first()
            
            if ai_enrichment:
                # Update existing enrichment
                ai_enrichment.category = ai_result['category']
                ai_enrichment.confidence_score = ai_result.get('confidence', 0.0)
                ai_enrichment.updated_at = datetime.now()
            else:
                # Create new enrichment
                ai_enrichment = AIEnrichment(
                    product_id=product.id,
                    category=ai_result['category'],
                    confidence_score=ai_result.get('confidence', 0.0),
                    model_used=self.ai_engine.llm.model_name if self.ai_engine.llm else 'mock',
                    generated_at=datetime.now()
                )
                session.add(ai_enrichment)
            
            # Log the AI processing
            self._log_categorization(session, product.id, ai_result, True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error categorizing product {product.id}: {e}")
            # Log the failure
            self._log_categorization(session, product.id, {}, False, str(e))
            return False
    
    def _log_categorization(self, session, product_id: int, ai_result: Dict[str, Any], 
                           success: bool, error_message: str = None):
        """Log categorization activity"""
        try:
            log_entry = AIProcessingLog(
                product_id=product_id,
                operation_type='categorization',
                model_used=ai_result.get('model_used', 'unknown'),
                success=success,
                error_message=error_message,
                processed_at=datetime.now()
            )
            session.add(log_entry)
            
        except Exception as e:
            logger.warning(f"Failed to log categorization: {e}")
    
    def recategorize_product(self, product_id: int) -> Dict[str, Any]:
        """Recategorize a specific product"""
        try:
            with self.db.get_session() as session:
                product = session.query(Product).filter(Product.id == product_id).first()
                
                if not product:
                    return {
                        'status': 'error',
                        'message': f'Product {product_id} not found'
                    }
                
                # Remove existing AI enrichment
                existing_enrichment = session.query(AIEnrichment).filter(
                    AIEnrichment.product_id == product_id
                ).first()
                
                if existing_enrichment:
                    session.delete(existing_enrichment)
                
                # Recategorize
                success = self._categorize_single_product(session, product)
                
                if success:
                    return {
                        'status': 'success',
                        'message': f'Product {product_id} recategorized successfully'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'Failed to recategorize product {product_id}'
                    }
                    
        except Exception as e:
            logger.error(f"Error recategorizing product {product_id}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_categorization_stats(self) -> Dict[str, Any]:
        """Get statistics about product categorization"""
        try:
            with self.db.get_session() as session:
                # Total products
                total_products = session.query(Product).count()
                
                # Products with AI categorization
                categorized_products = session.query(Product).join(AIEnrichment).count()
                
                # Category distribution
                category_counts = session.query(
                    AIEnrichment.category,
                    session.query(AIEnrichment).filter(AIEnrichment.category == AIEnrichment.category).count().label('count')
                ).group_by(AIEnrichment.category).all()
                
                # Confidence distribution
                high_confidence = session.query(AIEnrichment).filter(
                    AIEnrichment.confidence_score >= 0.8
                ).count()
                
                medium_confidence = session.query(AIEnrichment).filter(
                    AIEnrichment.confidence_score.between(0.5, 0.79)
                ).count()
                
                low_confidence = session.query(AIEnrichment).filter(
                    AIEnrichment.confidence_score < 0.5
                ).count()
                
                return {
                    'total_products': total_products,
                    'categorized_products': categorized_products,
                    'categorization_rate': (categorized_products / total_products * 100) if total_products > 0 else 0,
                    'category_distribution': {cat: count for cat, count in category_counts},
                    'confidence_distribution': {
                        'high': high_confidence,
                        'medium': medium_confidence,
                        'low': low_confidence
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting categorization stats: {e}")
            return {}
    
    def get_products_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get products by category"""
        try:
            with self.db.get_session() as session:
                products = session.query(Product, AIEnrichment).join(AIEnrichment).filter(
                    AIEnrichment.category == category
                ).limit(limit).all()
                
                result = []
                for product, enrichment in products:
                    result.append({
                        'id': product.id,
                        'title': product.title,
                        'price': product.price,
                        'currency': product.currency,
                        'image_url': product.image_url,
                        'source_url': product.source_url,
                        'category': enrichment.category,
                        'confidence': enrichment.confidence_score,
                        'scraped_at': product.scraped_at.isoformat() if product.scraped_at else None
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting products by category {category}: {e}")
            return []
    
    def export_categorization_data(self, format: str = 'json') -> str:
        """Export categorization data in specified format"""
        try:
            with self.db.get_session() as session:
                # Get all products with AI enrichment
                products = session.query(Product, AIEnrichment).join(AIEnrichment).all()
                
                data = []
                for product, enrichment in products:
                    data.append({
                        'product_id': product.id,
                        'title': product.title,
                        'price': product.price,
                        'currency': product.currency,
                        'category': enrichment.category,
                        'confidence': enrichment.confidence_score,
                        'scraped_at': product.scraped_at.isoformat() if product.scraped_at else None,
                        'categorized_at': enrichment.generated_at.isoformat() if enrichment.generated_at else None
                    })
                
                if format.lower() == 'json':
                    return json.dumps(data, indent=2)
                elif format.lower() == 'csv':
                    # Simple CSV export
                    csv_lines = ['product_id,title,price,currency,category,confidence,scraped_at,categorized_at']
                    for item in data:
                        csv_lines.append(f"{item['product_id']},\"{item['title']}\",{item['price']},{item['currency']},{item['category']},{item['confidence']},{item['scraped_at']},{item['categorized_at']}")
                    return '\n'.join(csv_lines)
                else:
                    raise ValueError(f"Unsupported format: {format}")
                    
        except Exception as e:
            logger.error(f"Error exporting categorization data: {e}")
            return ""


# Global instance
categorizer = ProductCategorizer()


def get_categorizer() -> ProductCategorizer:
    """Get categorizer instance"""
    return categorizer


if __name__ == "__main__":
    # Test the categorizer
    cat = get_categorizer()
    
    # Get stats
    stats = cat.get_categorization_stats()
    print(f"Categorization stats: {stats}")
    
    # Categorize some products
    result = cat.categorize_products(limit=5)
    print(f"Categorization result: {result}") 