"""
AI-powered product description generation module
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from database.connection import get_db
from database.models import Product, AIEnrichment, AIProcessingLog
from .langchain_chain import get_ai_engine

logger = logging.getLogger(__name__)


class DescriptionGenerator:
    """AI-powered product description generation system"""
    
    def __init__(self):
        self.db = get_db()
        self.ai_engine = get_ai_engine()
    
    def generate_descriptions(self, limit: int = 100, force_reprocess: bool = False) -> Dict[str, Any]:
        """Generate AI descriptions for multiple products"""
        start_time = datetime.now()
        
        try:
            with self.db.get_session() as session:
                # Get products that need description generation
                if force_reprocess:
                    # Get all products with AI enrichment
                    products = session.query(Product, AIEnrichment).join(AIEnrichment).limit(limit).all()
                else:
                    # Get products with AI enrichment but no AI description
                    products = session.query(Product, AIEnrichment).join(AIEnrichment).filter(
                        AIEnrichment.ai_description.is_(None)
                    ).limit(limit).all()
                
                if not products:
                    logger.info("No products found for description generation")
                    return {
                        'status': 'success',
                        'message': 'No products found for description generation',
                        'products_processed': 0,
                        'processing_time': (datetime.now() - start_time).total_seconds()
                    }
                
                logger.info(f"Starting description generation for {len(products)} products")
                
                processed_count = 0
                success_count = 0
                error_count = 0
                
                for product, enrichment in products:
                    try:
                        result = self._generate_single_description(session, product, enrichment)
                        if result:
                            success_count += 1
                        processed_count += 1
                        
                        # Log progress
                        if processed_count % 10 == 0:
                            logger.info(f"Processed {processed_count}/{len(products)} products")
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Failed to generate description for product {product.id}: {e}")
                        continue
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                logger.info(f"Description generation completed: {success_count} success, {error_count} errors, {processing_time:.2f}s")
                
                return {
                    'status': 'success',
                    'products_processed': processed_count,
                    'products_successful': success_count,
                    'products_failed': error_count,
                    'processing_time': processing_time
                }
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Description generation process failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'products_processed': 0,
                'products_successful': 0,
                'products_failed': 0,
                'processing_time': processing_time
            }
    
    def _generate_single_description(self, session, product: Product, enrichment: AIEnrichment) -> bool:
        """Generate AI description for a single product"""
        try:
            # Prepare product data for AI analysis
            title = product.title or ""
            price = product.price or 0.0
            description = product.short_description or ""
            
            # Get AI description generation
            ai_result = self.ai_engine.generate_description(title, price, description)
            
            if not ai_result:
                logger.warning(f"No AI result for product {product.id}")
                return False
            
            # Update AI enrichment record
            enrichment.ai_description = ai_result['description']
            enrichment.ai_tags = json.dumps(ai_result.get('tags', []))
            enrichment.updated_at = datetime.now()
            
            # Log the AI processing
            self._log_description_generation(session, product.id, ai_result, True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating description for product {product.id}: {e}")
            # Log the failure
            self._log_description_generation(session, product.id, {}, False, str(e))
            return False
    
    def _log_description_generation(self, session, product_id: int, ai_result: Dict[str, Any], 
                                  success: bool, error_message: str = None):
        """Log description generation activity"""
        try:
            log_entry = AIProcessingLog(
                product_id=product_id,
                operation_type='description',
                model_used=ai_result.get('model_used', 'unknown'),
                success=success,
                error_message=error_message,
                processed_at=datetime.now()
            )
            session.add(log_entry)
            
        except Exception as e:
            logger.warning(f"Failed to log description generation: {e}")
    
    def regenerate_description(self, product_id: int) -> Dict[str, Any]:
        """Regenerate AI description for a specific product"""
        try:
            with self.db.get_session() as session:
                product = session.query(Product).filter(Product.id == product_id).first()
                enrichment = session.query(AIEnrichment).filter(AIEnrichment.product_id == product_id).first()
                
                if not product:
                    return {
                        'status': 'error',
                        'message': f'Product {product_id} not found'
                    }
                
                if not enrichment:
                    return {
                        'status': 'error',
                        'message': f'Product {product_id} has no AI enrichment'
                    }
                
                # Clear existing AI description
                enrichment.ai_description = None
                enrichment.ai_tags = None
                
                # Regenerate
                success = self._generate_single_description(session, product, enrichment)
                
                if success:
                    return {
                        'status': 'success',
                        'message': f'Product {product_id} description regenerated successfully'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'Failed to regenerate description for product {product_id}'
                    }
                    
        except Exception as e:
            logger.error(f"Error regenerating description for product {product_id}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_description_stats(self) -> Dict[str, Any]:
        """Get statistics about AI description generation"""
        try:
            with self.db.get_session() as session:
                # Total products with AI enrichment
                total_enriched = session.query(Product).join(AIEnrichment).count()
                
                # Products with AI descriptions
                with_descriptions = session.query(Product).join(AIEnrichment).filter(
                    AIEnrichment.ai_description.isnot(None)
                ).count()
                
                # SEO score distribution
                high_seo = session.query(AIEnrichment).filter(
                    AIEnrichment.ai_description.isnot(None)
                ).count()  # Placeholder for SEO score filtering
                
                # Tag statistics
                all_tags = []
                tag_counts = {}
                
                enriched_products = session.query(AIEnrichment).filter(
                    AIEnrichment.ai_tags.isnot(None)
                ).all()
                
                for enrichment in enriched_products:
                    try:
                        tags = json.loads(enrichment.ai_tags or '[]')
                        all_tags.extend(tags)
                        for tag in tags:
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1
                    except:
                        continue
                
                # Get top tags
                top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                return {
                    'total_enriched_products': total_enriched,
                    'products_with_descriptions': with_descriptions,
                    'description_generation_rate': (with_descriptions / total_enriched * 100) if total_enriched > 0 else 0,
                    'total_tags_generated': len(all_tags),
                    'unique_tags': len(tag_counts),
                    'top_tags': dict(top_tags)
                }
                
        except Exception as e:
            logger.error(f"Error getting description stats: {e}")
            return {}
    
    def get_products_with_descriptions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get products with AI-generated descriptions"""
        try:
            with self.db.get_session() as session:
                products = session.query(Product, AIEnrichment).join(AIEnrichment).filter(
                    AIEnrichment.ai_description.isnot(None)
                ).limit(limit).all()
                
                result = []
                for product, enrichment in products:
                    tags = []
                    try:
                        tags = json.loads(enrichment.ai_tags or '[]')
                    except:
                        pass
                    
                    result.append({
                        'id': product.id,
                        'title': product.title,
                        'price': product.price,
                        'currency': product.currency,
                        'original_description': product.short_description,
                        'ai_description': enrichment.ai_description,
                        'tags': tags,
                        'category': enrichment.category,
                        'scraped_at': product.scraped_at.isoformat() if product.scraped_at else None,
                        'generated_at': enrichment.updated_at.isoformat() if enrichment.updated_at else None
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting products with descriptions: {e}")
            return []
    
    def compare_descriptions(self, product_id: int) -> Dict[str, Any]:
        """Compare original vs AI-generated description for a product"""
        try:
            with self.db.get_session() as session:
                product = session.query(Product, AIEnrichment).join(AIEnrichment).filter(
                    Product.id == product_id
                ).first()
                
                if not product:
                    return {
                        'status': 'error',
                        'message': f'Product {product_id} not found'
                    }
                
                product_obj, enrichment = product
                
                if not enrichment.ai_description:
                    return {
                        'status': 'error',
                        'message': f'Product {product_id} has no AI description'
                    }
                
                tags = []
                try:
                    tags = json.loads(enrichment.ai_tags or '[]')
                except:
                    pass
                
                return {
                    'status': 'success',
                    'product_id': product_id,
                    'title': product_obj.title,
                    'original_description': product_obj.short_description,
                    'ai_description': enrichment.ai_description,
                    'tags': tags,
                    'category': enrichment.category,
                    'comparison': {
                        'original_length': len(product_obj.short_description or ''),
                        'ai_length': len(enrichment.ai_description or ''),
                        'improvement_ratio': len(enrichment.ai_description or '') / max(len(product_obj.short_description or ''), 1)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error comparing descriptions for product {product_id}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def export_description_data(self, format: str = 'json') -> str:
        """Export AI description data in specified format"""
        try:
            with self.db.get_session() as session:
                # Get all products with AI descriptions
                products = session.query(Product, AIEnrichment).join(AIEnrichment).filter(
                    AIEnrichment.ai_description.isnot(None)
                ).all()
                
                data = []
                for product, enrichment in products:
                    tags = []
                    try:
                        tags = json.loads(enrichment.ai_tags or '[]')
                    except:
                        pass
                    
                    data.append({
                        'product_id': product.id,
                        'title': product.title,
                        'original_description': product.short_description,
                        'ai_description': enrichment.ai_description,
                        'tags': tags,
                        'category': enrichment.category,
                        'generated_at': enrichment.updated_at.isoformat() if enrichment.updated_at else None
                    })
                
                if format.lower() == 'json':
                    return json.dumps(data, indent=2)
                elif format.lower() == 'csv':
                    # Simple CSV export
                    csv_lines = ['product_id,title,original_description,ai_description,tags,category,generated_at']
                    for item in data:
                        tags_str = ';'.join(item['tags'])
                        csv_lines.append(f"{item['product_id']},\"{item['title']}\",\"{item['original_description']}\",\"{item['ai_description']}\",\"{tags_str}\",{item['category']},{item['generated_at']}")
                    return '\n'.join(csv_lines)
                else:
                    raise ValueError(f"Unsupported format: {format}")
                    
        except Exception as e:
            logger.error(f"Error exporting description data: {e}")
            return ""


# Global instance
description_generator = DescriptionGenerator()


def get_description_generator() -> DescriptionGenerator:
    """Get description generator instance"""
    return description_generator


if __name__ == "__main__":
    # Test the description generator
    gen = get_description_generator()
    
    # Get stats
    stats = gen.get_description_stats()
    print(f"Description generation stats: {stats}")
    
    # Generate descriptions for some products
    result = gen.generate_descriptions(limit=5)
    print(f"Description generation result: {result}") 