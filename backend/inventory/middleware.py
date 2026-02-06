"""
Custom middleware for the Inventory System.

This module contains middleware classes for handling
request/response processing.
"""

from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """
    Middleware to disable CSRF checks for API endpoints.
    
    This allows frontend applications to make POST, PUT, DELETE
    requests to API endpoints without CSRF tokens when using
    Token Authentication.
    """
    
    def process_request(self, request):
        """
        Mark API requests to skip CSRF verification.
        
        Sets _dont_enforce_csrf_checks attribute on requests
        that start with /api/ path.
        """
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
