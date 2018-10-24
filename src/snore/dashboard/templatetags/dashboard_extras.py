from django import template

from dashboard.models import Category


register = template.Library()

@register.filter
def change_color(value):
    if value%2 == 0:
        return True
    else:
        return False

@register.filter
def display_humantime(value):
    return value.strftime('%m-%d')

@register.inclusion_tag('dashboard/tags/login_pop.html')
def load_login_pop():
    # form = LoginForm()
    # return {'form': form}
    pass

@register.inclusion_tag('dashboard/tags/banner.html')
def load_banner():
    '''
    加载页面 顶部
    '''
    return {
        'categorys': Category.objects.all(),
    }

@register.inclusion_tag('dashboard/tags/sidebar_tag.html')
def load_sidebar_tag():
    '''
    加载侧边栏 标签
    '''
    # tags = Tag.objects.all()
    tags = ""
    return {
        'sidebar_tags': tags,
    }

@register.inclusion_tag('dashboard/tags/sidebar_new_goods.html')
def load_sidebar_flow_info():
    '''
    加载首页侧边栏 最新货源
    '''
    # articles = Article.published\
    #     .filter(category__is_goods=1, ad_property=0)[:12]
    articles = ""
    return {
        'sidebar_flow_info': [{'id': num+1, 'url': info.get_absolute_url, 'title': info.title}
                              for num, info in enumerate(articles)],
    }

@register.inclusion_tag('dashboard/tags/sidebar_recomm.html')
def load_sidebar_recomm():
    '''
    加载首页侧边栏 本站推荐
    '''
    # articles = Article.published.filter(ad_property=3)[:7]
    articles = ""
    return {
        'recomms': articles,
    }

@register.inclusion_tag('dashboard/tags/sidebar_source_goods.html')
def load_sidebar_source_goods():
    '''
    加载首页侧边栏 热门货源
    '''
    # articles = Article.published.filter(ad_property=0, category__is_goods=1)\
    #     .order_by('-views')[:7]
    articles = ""
    return {
        'goods': articles,
    }

@register.inclusion_tag('dashboard/tags/footer.html')
def load_footer():
    '''
    加载 footer
    '''
    from django.utils import timezone
    return {'year': timezone.now().year}

@register.inclusion_tag('dashboard/tags/scroll.html')
def load_scroll():
    '''
    加载 咨询栏
    '''
    return {
        # 'settings': SiteSettings.objects.get()
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
