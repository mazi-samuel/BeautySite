from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
import json
import logging

logger = logging.getLogger(__name__)


class ProductCache:
    """
    Utility class for caching product-related data
    """
    
    @staticmethod
    def get_product_list_cache_key(category_id=None, search_query=None, sort_by=None):
        """
        Generate a cache key for product lists
        """
        key_parts = ['products']
        
        if category_id:
            key_parts.append(f'category_{category_id}')
        
        if search_query:
            # Sanitize search query for cache key
            safe_query = ''.join(c for c in search_query if c.isalnum() or c in ' -_')
            key_parts.append(f'search_{safe_query}')
        
        if sort_by:
            key_parts.append(f'sort_{sort_by}')
        
        return ':'.join(key_parts)
    
    @staticmethod
    def get_product_detail_cache_key(product_id):
        """
        Generate a cache key for product details
        """
        return f'product_detail:{product_id}'
    
    @staticmethod
    def get_category_list_cache_key():
        """
        Generate a cache key for category lists
        """
        return 'categories'
    
    @staticmethod
    def get_popular_products_cache_key():
        """
        Generate a cache key for popular products
        """
        return 'popular_products'
    
    @staticmethod
    def cache_product_list(products, category_id=None, search_query=None, sort_by=None):
        """
        Cache a list of products
        """
        cache_key = ProductCache.get_product_list_cache_key(category_id, search_query, sort_by)
        cache.set(cache_key, products, timeout=settings.CACHE_TTL_PRODUCT_LIST)
        logger.info(f"Cached product list with key: {cache_key}")
    
    @staticmethod
    def get_cached_product_list(category_id=None, search_query=None, sort_by=None):
        """
        Retrieve cached product list
        """
        cache_key = ProductCache.get_product_list_cache_key(category_id, search_query, sort_by)
        products = cache.get(cache_key)
        if products:
            logger.info(f"Retrieved cached product list with key: {cache_key}")
        return products
    
    @staticmethod
    def cache_product_detail(product_data, product_id):
        """
        Cache product detail data
        """
        cache_key = ProductCache.get_product_detail_cache_key(product_id)
        cache.set(cache_key, product_data, timeout=settings.CACHE_TTL_PRODUCT_DETAIL)
        logger.info(f"Cached product detail with key: {cache_key}")
    
    @staticmethod
    def get_cached_product_detail(product_id):
        """
        Retrieve cached product detail
        """
        cache_key = ProductCache.get_product_detail_cache_key(product_id)
        product_data = cache.get(cache_key)
        if product_data:
            logger.info(f"Retrieved cached product detail with key: {cache_key}")
        return product_data
    
    @staticmethod
    def cache_category_list(categories):
        """
        Cache category list
        """
        cache_key = ProductCache.get_category_list_cache_key()
        cache.set(cache_key, categories, timeout=settings.CACHE_TTL_CATEGORY_LIST)
        logger.info(f"Cached category list with key: {cache_key}")
    
    @staticmethod
    def get_cached_category_list():
        """
        Retrieve cached category list
        """
        cache_key = ProductCache.get_category_list_cache_key()
        categories = cache.get(cache_key)
        if categories:
            logger.info(f"Retrieved cached category list with key: {cache_key}")
        return categories
    
    @staticmethod
    def cache_popular_products(products):
        """
        Cache popular products
        """
        cache_key = ProductCache.get_popular_products_cache_key()
        cache.set(cache_key, products, timeout=settings.CACHE_TTL_POPULAR_PRODUCTS)
        logger.info(f"Cached popular products with key: {cache_key}")
    
    @staticmethod
    def get_cached_popular_products():
        """
        Retrieve cached popular products
        """
        cache_key = ProductCache.get_popular_products_cache_key()
        products = cache.get(cache_key)
        if products:
            logger.info(f"Retrieved cached popular products with key: {cache_key}")
        return products
    
    @staticmethod
    def invalidate_product_cache(product_id=None, category_id=None):
        """
        Invalidate product-related cache entries
        """
        # Invalidate product detail cache
        if product_id:
            cache_key = ProductCache.get_product_detail_cache_key(product_id)
            cache.delete(cache_key)
            logger.info(f"Invalidated product detail cache with key: {cache_key}")
        
        # Invalidate product list caches (broad approach)
        # In a production environment, you might want to be more selective
        cache.delete_pattern('products:*')
        logger.info("Invalidated product list caches")
        
        # Invalidate popular products cache
        cache_key = ProductCache.get_popular_products_cache_key()
        cache.delete(cache_key)
        logger.info(f"Invalidated popular products cache with key: {cache_key}")
        
        # Invalidate category list cache if category changed
        if category_id:
            cache_key = ProductCache.get_category_list_cache_key()
            cache.delete(cache_key)
            logger.info(f"Invalidated category list cache with key: {cache_key}")


class SearchOptimizer:
    """
    Utility class for optimizing search functionality
    """
    
    @staticmethod
    def build_search_query(search_term):
        """
        Build an optimized search query
        """
        # Split search term into words
        words = search_term.split()
        
        # Build Q objects for each word
        queries = []
        for word in words:
            if len(word) >= 2:  # Only search for words with 2+ characters
                queries.append(
                    Q(name__icontains=word) |
                    Q(description__icontains=word)
                )
        
        # Combine queries with AND logic
        if queries:
            search_query = queries[0]
            for query in queries[1:]:
                search_query &= query
            return search_query
        
        return Q()  # Return empty query if no valid words
    
    @staticmethod
    def get_search_suggestions(search_term):
        """
        Get search suggestions based on cached popular searches
        """
        # In a real implementation, you would cache popular search terms
        # For now, we'll return an empty list
        return []
    
    @staticmethod
    def log_search_query(user, query, result_count):
        """
        Log search queries for analytics
        """
        from apps.analytics.models import SearchQuery
        
        try:
            SearchQuery.objects.create(
                user=user,
                query=query,
                result_count=result_count
            )
        except Exception as e:
            logger.error(f"Error logging search query: {e}")


class ImageOptimizer:
    """
    Utility class for optimizing image handling
    """
    
    @staticmethod
    def generate_thumbnail_url(image_url, size='medium'):
        """
        Generate thumbnail URL for different sizes
        """
        # In a real implementation, you would use an image processing library
        # For now, we'll just return the original URL with size parameter
        if '?' in image_url:
            return f"{image_url}&size={size}"
        else:
            return f"{image_url}?size={size}"
    
    @staticmethod
    def optimize_image_upload(image_file):
        """
        Optimize image upload (resize, compress, etc.)
        """
        # In a real implementation, you would use PIL or similar library
        # For now, we'll just return the original file
        return image_file


# Configuration for cache timeouts (in seconds)
CACHE_TTL_PRODUCT_LIST = 300  # 5 minutes
CACHE_TTL_PRODUCT_DETAIL = 600  # 10 minutes
CACHE_TTL_CATEGORY_LIST = 3600  # 1 hour
CACHE_TTL_POPULAR_PRODUCTS = 1800  # 30 minutes
