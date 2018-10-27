from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger

from .models import Category, Article, Tag, Link
from comments.forms import CommentForm

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


class IndexView(TemplateView):
    template_class = 'dashboard/index.html'

    def get(self, request):
        ads = Article.published.filter(~Q(ad_property=0))
        articles = Article.published.filter(ad_property=0, is_product=False)

        page = int(request.GET.get('page', 1))
        particles, page_range = paging(page, articles)

        context = {
            'ad_left_up_round': ads.filter(ad_property=1)[:6],
            'articles': particles,
            'page_range': page_range,
            'ad_column': ads.filter(ad_property=2)[0],
            'links': Link.objects.values('url', 'name'),
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
        article_comments = self.object.comment_list()
        # site_settings = SiteSettings.objects.get()

        kwargs['commentForm'] = CommentForm()
        kwargs['article_comments'] = article_comments
        # import pdb;pdb.set_trace()
        kwargs['articles'] = Article.published.filter(ad_property=5)[:4]

        aprev = Article.published.filter(id__lt=self.object.id, is_product=False).order_by('-id')
        kwargs['prev_article'] = aprev[0]  if aprev else ''
        anext = Article.published.filter(id__gt=self.object.id, is_product=False).order_by('id')
        kwargs['next_article'] = anext[0] if anext else ''

        # kwargs['wechat_pay_code'] = site_settings.wechat_pay_code
        # kwargs['alipay_code'] = site_settings.alipay_code
        context = super().get_context_data(**kwargs)
        return context


class ArticleListView(ListView):
    template_name = 'dashboard/category.html'
    context_object_name = 'articles'

    # 页面类型，分类目录或标签列表等
    page_type = ''

    def get_queryset(self):
        articles = self.get_queryset_data()
        return articles


class ArchiveView(ArticleListView):
    page_type = '帖文分类归档'

    def get_queryset_data(self):
        slug = self.kwargs['category']
        category = get_object_or_404(Category, slug=slug)
        category_name = category.name
        self.name = category_name
        articles = Article.published.filter(category__name=category_name)
        return articles

    def get_context_data(self, **kwargs):
        category_name = self.name
        kwargs['page_type'] = ArchiveView.page_type
        kwargs['tag_name'] = category_name

        category = Category.objects.get(name=category_name)
        kwargs['head_title'] = category.head_title
        kwargs['head_desc'] = category.head_desc
        kwargs['head_keywords'] = category.head_keywords
        kwargs['ad_column'] = Article.published.filter(ad_property=2)[0]

        page = int(self.request.GET.get('page', 1))
        particles, page_range = paging(page, self.object_list)
        kwargs['articles'] =  particles
        kwargs['page_range'] =  page_range
        return super(ArchiveView, self).get_context_data(**kwargs)


class TagDetailView(ArticleListView):
    page_type = '标签归档'
    paginate_by = 20

    def get_queryset_data(self):
        slug = self.kwargs['tag']
        tag = get_object_or_404(Tag, slug=slug)
        tag_name = tag.name
        self.name = tag_name
        article_list = Article.published.filter(tags__name=tag_name, ad_property=0)
        return article_list

    def get_context_data(self, **kwargs):
        tag_name = self.name
        kwargs['page_type'] = TagDetailView.page_type
        kwargs['tag_name'] = tag_name

        tag = Tag.objects.get(name=tag_name)
        kwargs['head_title'] = tag.head_title
        kwargs['head_desc'] = tag.head_desc
        kwargs['head_keywords'] = tag.head_keywords,
        return super(TagDetailView, self).get_context_data(**kwargs)

