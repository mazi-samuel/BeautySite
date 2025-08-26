"""beauty_marketplace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/auth/', include('apps.accounts.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/community/', include('apps.community.urls')),
    path('api/ads/', include('apps.advertisements.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),
    
    # Web URLs
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('products/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
    path('community/', include('apps.community.urls')),
    path('ads/', include('apps.advertisements.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
    
    # API documentation
    path('api/docs/', TemplateView.as_view(template_name='api_documentation.html'), name='api_docs'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
