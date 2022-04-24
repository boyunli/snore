"""snore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from snore.sitemap import StaticViewSitemap, ArticleSiteMap, \
    CategorySiteMap, TagSiteMap

sitemaps = {
    'static': StaticViewSitemap,
    'articles': ArticleSiteMap,
    'Category': CategorySiteMap,
    'Tag': TagSiteMap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'ckeditor/', include('ckeditor_uploader.urls')),
    path(r'', include('dashboard.urls', namespace='dashboard')),
    path('', include('comments.urls', namespace='comments')),
    path('tencent15876767698187748468.txt', TemplateView.as_view(
        template_name='sogousiteverification.txt', content_type="text/plain")),
    path('BingSiteAuth.xml', TemplateView.as_view(
        template_name='BingSiteAuth.xml', content_type="text/plain")),
    path(r'sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]

from django.conf.urls.static import static
from django.conf import settings
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
