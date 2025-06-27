"""
Comprehensive Error Handling Demonstration
This file shows all error handling patterns used in the project
"""

import redis
import logging
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandlingDemo:
    """Demonstrates all error handling patterns in the project"""
    
    def __init__(self):
        self.redis_client = None
        self.setup_redis()
    
    def setup_redis(self):
        """1. Cache Connection Error Handling"""
        try:
            self.redis_client = redis.Redis(
                host="localhost", 
                port=6379, 
                db=0, 
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.redis_client = None
        except Exception as e:
            logger.error(f"❌ Unexpected Redis error: {e}")
            self.redis_client = None
    
    def cache_operation_with_fallback(self, key: str, data: dict = None):
        """2. Cache Operation Error Handling with Fallback"""
        if not self.redis_client:
            logger.info("Cache not available - using fallback")
            return None
        
        try:
            if data:  # SET operation
                self.redis_client.setex(key, 300, str(data))
                logger.info(f"✅ Cached data for key: {key}")
                return True
            else:  # GET operation
                cached_data = self.redis_client.get(key)
                if cached_data:
                    logger.info(f"✅ Cache hit for key: {key}")
                    return cached_data
                else:
                    logger.info(f"ℹ️ Cache miss for key: {key}")
                    return None
                    
        except redis.exceptions.ConnectionError:
            logger.warning("⚠️ Redis connection lost during operation")
            return None
        except redis.exceptions.TimeoutError:
            logger.warning("⚠️ Redis operation timed out")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected cache error: {e}")
            return None
    
    def database_operation_with_error_handling(self, db_session, operation_type: str):
        """3. Database Error Handling"""
        try:
            if operation_type == "create":
                # Simulate database operation
                result = {"id": 1, "title": "Test Book"}
                logger.info("✅ Database operation successful")
                return result
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error: {e}")
            db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected database error: {e}")
            db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def api_validation_error_handling(self, request_data: dict):
        """4. API Input Validation Error Handling"""
        try:
            # Simulate Pydantic validation
            if not request_data.get("title"):
                raise ValidationError("Title is required", model=None)
            
            if len(request_data.get("title", "")) > 255:
                raise ValidationError("Title too long", model=None)
                
            logger.info("✅ Validation successful")
            return True
            
        except ValidationError as e:
            logger.warning(f"⚠️ Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {e}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request data"
            )
    
    def comprehensive_error_demo(self):
        """5. Complete Error Handling Flow"""
        logger.info("🚀 Starting comprehensive error handling demo")
        
        # Test cache errors
        logger.info("\n--- Testing Cache Error Handling ---")
        self.cache_operation_with_fallback("test:key")
        
        # Test validation errors  
        logger.info("\n--- Testing Validation Error Handling ---")
        try:
            self.api_validation_error_handling({"title": ""})
        except HTTPException as e:
            logger.info(f"Caught validation error: {e.detail}")
        
        # Test database errors
        logger.info("\n--- Testing Database Error Handling ---")
        try:
            self.database_operation_with_error_handling(None, "create")
        except HTTPException as e:
            logger.info(f"Caught database error: {e.detail}")
        
        logger.info("✅ Error handling demo completed")

# Usage example
if __name__ == "__main__":
    demo = ErrorHandlingDemo()
    demo.comprehensive_error_demo()
