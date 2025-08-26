from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.conf import settings
import re


class SecurityMiddleware(MiddlewareMixin):
    """
    Custom security middleware to enhance application security
    """
    
    def process_request(self, request):
        # Check for suspicious patterns in the request
        if self._is_suspicious_request(request):
            return HttpResponseForbidden("Suspicious request detected")
        
        # Add security headers
        return None
    
    def process_response(self, request, response):
        # Add security headers to the response
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response['Content-Security-Policy'] = csp_policy
        
        return response
    
    def _is_suspicious_request(self, request):
        """
        Check if the request contains suspicious patterns
        """
        # Check for SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|\/\*|\*\/|;)",
        ]
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
        ]
        
        # Combine all patterns
        all_patterns = sql_patterns + xss_patterns
        
        # Check path, GET parameters, and POST data
        check_strings = [
            request.path,
            str(request.GET),
            str(request.POST),
        ]
        
        for pattern in all_patterns:
            for check_string in check_strings:
                if re.search(pattern, check_string, re.IGNORECASE):
                    return True
        
        return False


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}  # In production, use Redis or database
        
    def process_request(self, request):
        ip = self._get_client_ip(request)
        
        # Check if IP is in our requests dict
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Get current timestamp
        import time
        now = time.time()
        
        # Remove requests older than 1 hour
        self.requests[ip] = [req_time for req_time in self.requests[ip] if now - req_time < 3600]
        
        # Check if limit exceeded (100 requests per hour)
        if len(self.requests[ip]) >= 100:
            return HttpResponseForbidden("Rate limit exceeded")
        
        # Add current request
        self.requests[ip].append(now)
        
        return None
    
    def _get_client_ip(self, request):
        """
        Get the client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip