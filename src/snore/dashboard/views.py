from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Category, Article, Tag, Link

class IndexView(TemplateView):
    template_class = 'dashboard/index.html'

    def get(self, request):
        ads = Article.published.filter(~Q(ad_property=0))
        articles = Article.published.filter(ad_property=0)
        # import pdb;pdb.set_trace()
        context = {
            'ad_left_up_round': ads.filter(ad_property=1)[:6],
            'new_articles': articles[:10],
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

        # kwargs['commentForm'] = CommentForm()
        kwargs['article_comments'] = article_comments
        kwargs['articles'] = Article.published.filter(ad_property=5)[:4]
        kwargs['sim_articles'] = Article.published.filter(category=kwargs['object'].category, ad_property=0)[:5]
        kwargs['best_articles'] = Article.published.filter(ad_property=0, category__is_goods=1).order_by('-views')[:5]
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
    paginate_by = 20

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

