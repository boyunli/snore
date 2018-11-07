from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(r'category/<slug:category>.html', views.ArchiveView.as_view(), name='category'),
    path(r'tag/<slug:tag>.html', views.TagDetailView.as_view(), name='tag'),
    path(r'article/<int:article_id>.html',
         views.ArticleDetailView.as_view(), name='article'),
]
