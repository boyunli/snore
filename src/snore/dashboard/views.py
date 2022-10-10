from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger

from .models import Category, Article, Tag, Link, SiteSettings
from comments.forms import CommentForm

settings = SiteSettings.load()


def paging(page, items, display_amount=15,
           after_range_num=5, bevor_range_num=4):
    paginator = Paginator(items, display_amount)
    try:
        items = paginator.page(page)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    except (InvalidPage, PageNotAnInteger):
        items = paginator.page(1)
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+bevor_range_num]
    else:
        page_range = paginator.page_range[0:page+bevor_range_num]
    return items, page_range


def page_not_found(request, **kwargs):
    return render(request, '404.html')


class SearchView(TemplateView):
    template_class = 'search/search.html'

    def get(self, request):
        query = request.GET.get('q')
        articles = Article.published.filter(Q(title__icontains=query))

        page = int(self.request.GET.get('page', 1))
        particles, page_range = paging(page, articles)
        context = {
            'articles': particles,
            'page_range': page_range,
            "query": query,
            'settings': settings,

        }
        return render(request, self.template_class, context)


class IndexView(TemplateView):
    template_class = 'dashboard/index.html'

    def get(self, request):
        ads = Article.published.filter(~Q(ad_property=0))
        articles = Article.published.exclude(ad_property__in=[1, 2, 3]).filter(is_home_display=True)

        page = int(request.GET.get('page', 1))
        particles, page_range = paging(page, articles)

        ad_column = ads.filter(ad_property=2)
        context = {
            'settings': settings,
            'bd_articles': Article.published.filter(is_broadcast=True),
            'ad_left_up_round': ads.filter(ad_property=1)[:6],
            'articles': particles,
            'page_range': page_range,
            'ad_column': ad_column[0] if ad_column else None,
            'links': Link.objects.values('url', 'name'),
            'page': page,
        }
        return render(request, self.template_class, context)


class ArticleDetailView(DetailView):
    template_name = 'dashboard/article.html'
    model = Article
    context_object_name = 'article'
    pk_url_kwarg = 'article_id'

    def get_object(self):
        obj = super().get_object()
        obj.viewed()
        obj.image = Article.objects.get(id=int(self.kwargs[self.pk_url_kwarg])).image
        self.object = obj
        return obj

    def get_context_data(self, **kwargs):
        kwargs['settings'] = settings
        kwargs['commentForm'] = CommentForm()
        kwargs['article_comments'] = self.object.comment_list()
        # import pdb;pdb.set_trace()
        kwargs['articles'] = Article.published.filter(ad_property=5)[:4]

        aprev = Article.published.filter(id__lt=self.object.id, is_product=False).order_by('-id')
        kwargs['prev_article'] = aprev[0] if aprev else ''
        anext = Article.published.filter(id__gt=self.object.id, is_product=False).order_by('id')
        kwargs['next_article'] = anext[0] if anext else ''

        context = super().get_context_data(**kwargs)
        return context


class ArticleListView(ListView):
    template_name = 'dashboard/category.html'
    context_object_name = 'articles'
    page_type = None

    def get_queryset(self):
        articles = self.get_queryset_data()
        return articles

    def get_context_data(self, **kwargs):
        kwargs['tag_name'] = self.name
        kwargs['has_intro'] = False
        if self.page_type == 'category':
            item = Category.objects.get(name=self.name)
        elif self.page_type == 'tag':
            item = Tag.objects.get(name=self.name)
            if item.title != 'null':
                kwargs['has_intro'] = True
                kwargs['tag_title'] = item.title
                kwargs['tag_intro'] = item.intro
                kwargs['tag_date'] = item.update_time
                kwargs['tag_count'] = item.article_set.count()
        kwargs['head_title'] = item.head_title
        kwargs['head_desc'] = item.head_desc
        kwargs['head_keywords'] = item.head_keywords

        ad_column = Article.published.filter(ad_property=3)
        if ad_column:
            kwargs['ad_column'] = ad_column[0]
        page = int(self.request.GET.get('page', 1))
        particles, page_range = paging(page, self.object_list)
        kwargs['articles'] = particles
        kwargs['page_range'] = page_range
        kwargs['settings'] = settings
        kwargs['page'] = page
        return super(ArticleListView, self).get_context_data(**kwargs)


class ArchiveView(ArticleListView):
    page_type = 'category'

    def get_queryset_data(self):
        slug = self.kwargs['category']
        category = get_object_or_404(Category, slug=slug)
        self.name = category.name
        articles = Article.published.filter(category__name=category.name)\
            .exclude(ad_property__in=[1,2,3])
        return articles


class TagDetailView(ArticleListView):
    page_type = 'tag'

    def get_queryset_data(self):
        slug = self.kwargs['tag']
        tag = get_object_or_404(Tag, slug=slug)
        self.name = tag.name
        articles = Article.published.filter(tags__name=tag.name)\
            .exclude(ad_property__in=[1,2,3])
        return articles

