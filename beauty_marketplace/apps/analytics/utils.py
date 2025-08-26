import time
import logging
from functools import wraps
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Utility class for monitoring application performance
    """
    
    @staticmethod
    def timing_decorator(func):
        """
        Decorator to measure function execution time
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            
            # Store timing in cache for monitoring
            cache_key = f"timing:{func.__name__}"
            cache.set(cache_key, execution_time, timeout=3600)  # Cache for 1 hour
            
            return result
        return wrapper
    
    @staticmethod
    def database_query_count(func):
        """
        Decorator to count database queries
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            initial_queries = len(connection.queries)
            result = func(*args, **kwargs)
            final_queries = len(connection.queries)
            
            query_count = final_queries - initial_queries
            logger.info(f"{func.__name__} executed {query_count} database queries")
            
            # Store query count in cache for monitoring
            cache_key = f"queries:{func.__name__}"
            cache.set(cache_key, query_count, timeout=3600)  # Cache for 1 hour
            
            return result
        return wrapper
    
    @staticmethod
    def get_performance_metrics():
        """
        Get current performance metrics
        """
        # Get cached timing data
        timing_keys = cache.keys("timing:*")
        timings = {}
        for key in timing_keys:
            func_name = key.replace("timing:", "")
            timings[func_name] = cache.get(key)
        
        # Get cached query count data
        query_keys = cache.keys("queries:*")
        queries = {}
        for key in query_keys:
            func_name = key.replace("queries:", "")
            queries[func_name] = cache.get(key)
        
        return {
            'timings': timings,
            'queries': queries
        }


class MemoryMonitor:
    """
    Utility class for monitoring memory usage
    """
    
    @staticmethod
    def log_memory_usage(location=""):
        """
        Log current memory usage
        """
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            logger.info(f"Memory usage at {location}: {memory_info.rss / 1024 / 1024:.2f} MB")
        except ImportError:
            logger.warning("psutil not installed, skipping memory monitoring")
        except Exception as e:
            logger.error(f"Error monitoring memory usage: {e}")


class CacheMonitor:
    """
    Utility class for monitoring cache performance
    """
    
    @staticmethod
    def log_cache_hit_rate():
        """
        Log cache hit rate (simplified implementation)
        """
        # In a real implementation, you would track cache hits/misses
        # This is a placeholder for demonstration
        logger.info("Cache monitoring placeholder")


class UserActivityTracker:
    """
    Utility class for tracking user activity
    """
    
    @staticmethod
    def track_user_activity(user, activity_type, description="", ip_address=None, user_agent=None):
        """
        Track user activity for analytics
        """
        from apps.analytics.models import UserActivity
        
        try:
            UserActivity.objects.create(
                user=user,
                activity_type=activity_type,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Error tracking user activity: {e}")
    
    @staticmethod
    def track_product_view(user, product_id, ip_address=None, user_agent=None):
        """
        Track product views
        """
        from apps.analytics.models import ProductView
        
        try:
            ProductView.objects.create(
                product_id=product_id,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Error tracking product view: {e}")
    
    @staticmethod
    def track_user_signup():
        """
        Track user signups
        """
        from apps.analytics.models import UserSignup
        
        try:
            today = timezone.now().date()
            signup, created = UserSignup.objects.get_or_create(
                date=today,
                defaults={'signup_count': 1}
            )
            
            if not created:
                signup.signup_count += 1
                signup.save()
        except Exception as e:
            logger.error(f"Error tracking user signup: {e}")


class RevenueTracker:
    """
    Utility class for tracking revenue
    """
    
    @staticmethod
    def track_order_revenue(order):
        """
        Track revenue from an order
        """
        from apps.analytics.models import RevenueReport
        
        try:
            order_date = order.created_at.date()
            report, created = RevenueReport.objects.get_or_create(
                date=order_date,
                defaults={
                    'total_revenue': order.total_amount,
                    'order_count': 1,
                    'product_count': order.items.count()
                }
            )
            
            if not created:
                report.total_revenue += order.total_amount
                report.order_count += 1
                report.product_count += order.items.count()
                report.save()
        except Exception as e:
            logger.error(f"Error tracking order revenue: {e}")
