from django import template

from dashboard.models import Category, Article, Tag
from dashboard.views import settings
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def highlight_query(title, query):
    return format_html(title.replace(query,'<span class="highlighted">{}</span>'), query)

@register.filter
def display_humantime(value):
    return value.strftime('%m-%d')

@register.inclusion_tag('dashboard/tags/banner.html')
def load_banner():
    '''
    加载页面 顶部
    '''
    return {
        'categorys': Category.objects.all(),
        'settings': settings
    }

@register.inclusion_tag('dashboard/tags/sidebar_tag.html')
def load_sidebar_tag():
    '''
    加载侧边栏 标签
    '''
    tags = Tag.objects.all()
    return {
        'sidebar_tags': tags,
    }

@register.inclusion_tag('dashboard/tags/sidebar_hot.html')
def load_sidebar_hot():
    '''
    加载首页侧边栏 热门文章
    '''
    return {
        'hot_articles': Article.published.filter(ad_property=0).order_by('-views')[:10],
    }

@register.inclusion_tag('dashboard/tags/sidebar_best_recomm.html')
def load_sidebar_best_recomm():
    '''
    加载首页侧边栏 优质推荐
    '''
    return {
        'best_articles': Article.published.filter(ad_property=4)[:10]
    }

@register.inclusion_tag('dashboard/tags/footer.html')
def load_footer():
    '''
    加载 footer
    '''
    from django.utils import timezone
    return {
        'year': timezone.now().year,
        'settings': settings
    }

@register.inclusion_tag('dashboard/tags/scroll.html')
def load_scroll():
    '''
    加载 咨询栏
    '''
    return {
        'settings': settings
    }

@register.simple_tag
def query(qs, **kwargs):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return qs.filter(**kwargs)
