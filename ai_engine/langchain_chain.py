"""
LangChain integration for AI-powered product analysis
"""
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from config.settings import OPENROUTER_CONFIG, AI_PROMPTS, PRODUCT_CATEGORIES
from database.connection import get_db
from database.models import AIProcessingLog

logger = logging.getLogger(__name__)


class ProductCategory(BaseModel):
    """Pydantic model for product categorization output"""
    category: str = Field(description="The product category")
    confidence: float = Field(description="Confidence score from 0 to 1")
    reasoning: str = Field(description="Brief reasoning for the categorization")


class ProductDescription(BaseModel):
    """Pydantic model for AI-generated description output"""
    description: str = Field(description="Enhanced product description")
    tags: List[str] = Field(description="Relevant tags for the product")
    seo_score: int = Field(description="SEO optimization score from 1 to 10")


class AnomalyAnalysis(BaseModel):
    """Pydantic model for anomaly detection output"""
    risk_score: int = Field(description="Risk score from 1 to 10")
    anomalies: List[str] = Field(description="List of detected anomalies")
    recommendations: List[str] = Field(description="Recommendations for improvement")


class LangChainEngine:
    """Main engine for AI-powered product analysis using LangChain"""
    
    def __init__(self):
        self.db = get_db()
        self.llm = None
        self.setup_llm()
        self.setup_chains()
    
    def setup_llm(self):
        """Setup the language model"""
        try:
            # Use OpenRouter for model access
            self.llm = ChatOpenAI(
                openai_api_base="https://openrouter.ai/api/v1",
                openai_api_key=OPENROUTER_CONFIG['api_key'],
                model_name=OPENROUTER_CONFIG['model'],
                max_tokens=OPENROUTER_CONFIG['max_tokens'],
                temperature=OPENROUTER_CONFIG['temperature'],
                request_timeout=60
            )
            logger.info("Language model setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup language model: {e}")
            # Fallback to mock mode for development
            self.llm = None
            logger.warning("Running in mock mode - no actual AI calls will be made")
    
    def setup_chains(self):
        """Setup LangChain chains for different operations"""
        try:
            if self.llm:
                # Categorization chain
                self.categorization_chain = LLMChain(
                    llm=self.llm,
                    prompt=ChatPromptTemplate.from_template(AI_PROMPTS['categorization'])
                )
                
                # Description generation chain
                self.description_chain = LLMChain(
                    llm=self.llm,
                    prompt=ChatPromptTemplate.from_template(AI_PROMPTS['description_generation'])
                )
                
                # Anomaly detection chain
                self.anomaly_chain = LLMChain(
                    llm=self.llm,
                    prompt=ChatPromptTemplate.from_template(AI_PROMPTS['anomaly_detection'])
                )
                
                logger.info("LangChain chains setup completed")
            else:
                logger.warning("LangChain chains not setup due to missing LLM")
                
        except Exception as e:
            logger.error(f"Failed to setup LangChain chains: {e}")
    
    def categorize_product(self, title: str, description: str = "") -> Dict[str, Any]:
        """Categorize a product using AI"""
        start_time = time.time()
        
        try:
            if not self.llm:
                # Mock categorization for development
                return self._mock_categorization(title, description)
            
            # Prepare prompt
            prompt_vars = {
                'categories': ', '.join(PRODUCT_CATEGORIES),
                'title': title,
                'description': description or "No description available"
            }
            
            # Get AI response
            response = self.categorization_chain.run(prompt_vars)
            
            # Parse response
            category_result = self._parse_categorization_response(response)
            
            # Log processing
            processing_time = time.time() - start_time
            self._log_ai_processing(
                operation_type='categorization',
                success=True,
                processing_time=processing_time
            )
            
            return category_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Product categorization failed: {e}")
            
            # Log failure
            self._log_ai_processing(
                operation_type='categorization',
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            
            # Return fallback categorization
            return self._fallback_categorization(title, description)
    
    def generate_description(self, title: str, price: float, description: str = "") -> Dict[str, Any]:
        """Generate enhanced product description using AI"""
        start_time = time.time()
        
        try:
            if not self.llm:
                # Mock description generation for development
                return self._mock_description_generation(title, price, description)
            
            # Prepare prompt
            prompt_vars = {
                'title': title,
                'price': f"${price:.2f}" if price else "Price not available",
                'description': description or "No description available"
            }
            
            # Get AI response
            response = self.description_chain.run(prompt_vars)
            
            # Parse response
            description_result = self._parse_description_response(response)
            
            # Log processing
            processing_time = time.time() - start_time
            self._log_ai_processing(
                operation_type='description',
                success=True,
                processing_time=processing_time
            )
            
            return description_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Description generation failed: {e}")
            
            # Log failure
            self._log_ai_processing(
                operation_type='description',
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            
            # Return fallback description
            return self._fallback_description_generation(title, price, description)
    
    def detect_anomalies(self, title: str, price: float, category: str, description: str = "") -> Dict[str, Any]:
        """Detect anomalies in product data using AI"""
        start_time = time.time()
        
        try:
            if not self.llm:
                # Mock anomaly detection for development
                return self._mock_anomaly_detection(title, price, category, description)
            
            # Prepare prompt
            prompt_vars = {
                'title': title,
                'price': f"${price:.2f}" if price else "Price not available",
                'category': category,
                'description': description or "No description available"
            }
            
            # Get AI response
            response = self.anomaly_chain.run(prompt_vars)
            
            # Parse response
            anomaly_result = self._parse_anomaly_response(response)
            
            # Log processing
            processing_time = time.time() - start_time
            self._log_ai_processing(
                operation_type='anomaly',
                success=True,
                processing_time=processing_time
            )
            
            return anomaly_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Anomaly detection failed: {e}")
            
            # Log failure
            self._log_ai_processing(
                operation_type='anomaly',
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            
            # Return fallback anomaly detection
            return self._fallback_anomaly_detection(title, price, category, description)
    
    def _parse_categorization_response(self, response: str) -> Dict[str, Any]:
        """Parse AI categorization response"""
        try:
            # Try to extract category from response
            response_lower = response.lower().strip()
            
            # Find matching category
            for category in PRODUCT_CATEGORIES:
                if category.lower() in response_lower:
                    return {
                        'category': category,
                        'confidence': 0.85,  # Default confidence
                        'reasoning': f"AI classified as {category} based on title and description"
                    }
            
            # Fallback to 'Other' if no match found
            return {
                'category': 'Other',
                'confidence': 0.5,
                'reasoning': "AI response didn't match predefined categories"
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse categorization response: {e}")
            return self._fallback_categorization("", "")
    
    def _parse_description_response(self, response: str) -> Dict[str, Any]:
        """Parse AI description generation response"""
        try:
            # Extract description from response
            lines = response.strip().split('\n')
            description = lines[0] if lines else "Enhanced description not available"
            
            # Generate tags from title and description
            tags = self._extract_tags(description)
            
            return {
                'description': description,
                'tags': tags,
                'seo_score': 8  # Default SEO score
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse description response: {e}")
            return self._fallback_description_generation("", 0, "")
    
    def _parse_anomaly_response(self, response: str) -> Dict[str, Any]:
        """Parse AI anomaly detection response"""
        try:
            # Extract risk score from response
            risk_score = 5  # Default risk score
            
            # Look for risk indicators in response
            response_lower = response.lower()
            if 'high' in response_lower or 'risk' in response_lower:
                risk_score = 8
            elif 'low' in response_lower or 'safe' in response_lower:
                risk_score = 2
            
            return {
                'risk_score': risk_score,
                'anomalies': ["AI analysis completed"],
                'recommendations': ["Review product data for accuracy"]
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse anomaly response: {e}")
            return self._fallback_anomaly_detection("", 0, "", "")
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        # Simple tag extraction - in production, use more sophisticated NLP
        words = text.lower().split()
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        tags = []
        for word in words:
            if len(word) > 3 and word not in common_words:
                tags.append(word)
                if len(tags) >= 5:  # Limit to 5 tags
                    break
        
        return tags[:5]
    
    def _log_ai_processing(self, operation_type: str, success: bool, 
                          processing_time: float = None, error_message: str = None):
        """Log AI processing activities"""
        try:
            with self.db.get_session() as session:
                log_entry = AIProcessingLog(
                    product_id=1,  # Placeholder - should be actual product ID
                    operation_type=operation_type,
                    model_used=OPENROUTER_CONFIG['model'] if self.llm else 'mock',
                    processing_time=processing_time,
                    success=success,
                    error_message=error_message
                )
                session.add(log_entry)
                session.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log AI processing: {e}")
    
    # Mock methods for development/testing
    def _mock_categorization(self, title: str, description: str) -> Dict[str, Any]:
        """Mock categorization for development"""
        # Simple rule-based categorization
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['book', 'novel', 'story', 'fiction']):
            category = 'Books'
        elif any(word in title_lower for word in ['phone', 'laptop', 'computer', 'electronic']):
            category = 'Electronics'
        elif any(word in title_lower for word in ['shirt', 'pants', 'dress', 'shoes']):
            category = 'Clothing'
        else:
            category = 'Other'
        
        return {
            'category': category,
            'confidence': 0.75,
            'reasoning': f"Mock categorization based on keywords in title: {title[:50]}..."
        }
    
    def _mock_description_generation(self, title: str, price: float, description: str) -> Dict[str, Any]:
        """Mock description generation for development"""
        mock_description = f"Discover the amazing {title}! This high-quality product offers exceptional value at ${price:.2f}. Perfect for your needs with premium features and outstanding performance."
        
        return {
            'description': mock_description,
            'tags': ['premium', 'quality', 'value', 'performance'],
            'seo_score': 7
        }
    
    def _mock_anomaly_detection(self, title: str, price: float, category: str, description: str) -> Dict[str, Any]:
        """Mock anomaly detection for development"""
        risk_score = 3  # Low risk by default
        
        if price and price < 1.0:  # Very low price
            risk_score = 8
        elif price and price > 1000.0:  # Very high price
            risk_score = 6
        
        return {
            'risk_score': risk_score,
            'anomalies': ["Mock analysis completed"],
            'recommendations': ["Review pricing strategy", "Verify product information"]
        }
    
    # Fallback methods
    def _fallback_categorization(self, title: str, description: str) -> Dict[str, Any]:
        """Fallback categorization when AI fails"""
        return {
            'category': 'Other',
            'confidence': 0.3,
            'reasoning': 'Fallback categorization due to AI processing failure'
        }
    
    def _fallback_description_generation(self, title: str, price: float, description: str) -> Dict[str, Any]:
        """Fallback description generation when AI fails"""
        return {
            'description': f"Product: {title}. Price: ${price:.2f}. {description}",
            'tags': ['product', 'available'],
            'seo_score': 3
        }
    
    def _fallback_anomaly_detection(self, title: str, price: float, category: str, description: str) -> Dict[str, Any]:
        """Fallback anomaly detection when AI fails"""
        return {
            'risk_score': 5,
            'anomalies': ['Analysis unavailable'],
            'recommendations': ['Manual review recommended']
        }


# Global instance
ai_engine = LangChainEngine()


def get_ai_engine() -> LangChainEngine:
    """Get AI engine instance"""
    return ai_engine


if __name__ == "__main__":
    # Test the AI engine
    engine = get_ai_engine()
    
    # Test categorization
    result = engine.categorize_product("Wireless Bluetooth Headphones", "High-quality wireless headphones with noise cancellation")
    print(f"Categorization: {result}")
    
    # Test description generation
    result = engine.generate_description("Wireless Bluetooth Headphones", 99.99, "High-quality wireless headphones")
    print(f"Description: {result}")
    
    # Test anomaly detection
    result = engine.detect_anomalies("Wireless Bluetooth Headphones", 99.99, "Electronics", "High-quality wireless headphones")
    print(f"Anomaly: {result}") 