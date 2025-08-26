from django.db import models
from django.db.models import Q, Count, Avg
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ProductManager(models.Manager):
    """
    Custom manager for Product model with optimized queries
    """
    
    def get_active_products(self):
        """
        Get all active products
        """
        return self.filter(is_active=True)
    
    def get_products_by_category(self, category_id):
        """
        Get products by category with optimization
        """
        return self.filter(category_id=category_id, is_active=True).select_related('seller')
    
    def get_products_with_images(self):
        """
        Get products with their images prefetched
        """
        return self.filter(is_active=True).prefetch_related('images')
    
    def search_products(self, query):
        """
        Search products with optimization
        """
        if not query:
            return self.get_active_products()
        
        # Split query into words and build search conditions
        words = query.split()
        search_conditions = Q()
        
        for word in words:
            if len(word) >= 2:  # Only search for words with 2+ characters
                search_conditions |= (
                    Q(name__icontains=word) |
                    Q(description__icontains=word)
                )
        
        return self.filter(search_conditions, is_active=True).select_related('seller')
    
    def get_popular_products(self, limit=10):
        """
        Get popular products based on reviews and sales
        """
        return self.filter(is_active=True).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).filter(
            review_count__gt=0
        ).order_by('-avg_rating', '-review_count')[:limit]
    
    def get_featured_products(self, limit=8):
        """
        Get featured products (newest with good ratings)
        """
        return self.filter(is_active=True).annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).filter(
            review_count__gte=3,  # At least 3 reviews
            avg_rating__gte=4.0   # At least 4 star average
        ).order_by('-created_at')[:limit]


class CategoryManager(models.Manager):
    """
    Custom manager for Category model with optimized queries
    """
    
    def get_active_categories(self):
        """
        Get all active categories
        """
        return self.filter(is_active=True)
    
    def get_categories_with_product_counts(self):
        """
        Get categories with product counts
        """
        return self.get_active_categories().annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).filter(product_count__gt=0).order_by('name')


class ProductImageManager(models.Manager):
    """
    Custom manager for ProductImage model with optimized queries
    """
    
    def get_primary_images(self):
        """
        Get all primary images
        """
        return self.filter(is_primary=True)
    
    def get_images_for_products(self, product_ids):
        """
        Get images for multiple products efficiently
        """
        return self.filter(product_id__in=product_ids).select_related('product')


class ProductReviewManager(models.Manager):
    """
    Custom manager for ProductReview model with optimized queries
    """
    
    def get_reviews_for_product(self, product_id):
        """
        Get reviews for a specific product with user information
        """
        return self.filter(product_id=product_id).select_related('user__profile')
    
    def get_recent_reviews(self, limit=10):
        """
        Get most recent reviews
        """
        return self.select_related('user__profile', 'product').order_by('-created_at')[:limit]
    
    def get_user_reviews(self, user_id):
        """
        Get all reviews by a specific user
        """
        return self.filter(user_id=user_id).select_related('product')


# Additional database optimization utilities
class DatabaseOptimizer:
    """
    Utility class for database optimization
    """
    
    @staticmethod
    def optimize_product_queries(queryset):
        """
        Apply common optimizations to product queries
        """
        return queryset.select_related('seller', 'category').prefetch_related('images')
    
    @staticmethod
    def optimize_category_queries(queryset):
        """
        Apply common optimizations to category queries
        """
        return queryset.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )
    
    @staticmethod
    def optimize_review_queries(queryset):
        """
        Apply common optimizations to review queries
        """
        return queryset.select_related('user__profile', 'product')
    
    @staticmethod
    def get_products_with_review_stats():
        """
        Get products with review statistics
        """
        return ProductManager().get_queryset().annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        )