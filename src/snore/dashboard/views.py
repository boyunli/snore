from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from .models import Category

class IndexView(TemplateView):
    template_class = 'dashboard/index.html'

    def get(self, request):
        context = {
            'categorys': Category.objects.all()
        }
        return render(request, self.template_class, context)


class ArticleListView(ListView):
    template_name = 'dashboard/article_archive.html'
    context_object_name = 'article_list'

    # 页面类型，分类目录或标签列表等
    page_type = ''

    def get_queryset(self):
        article_list = self.get_queryset_data()
        return article_list


class ArchiveView(ArticleListView):
    page_type = '帖文分类归档'
    paginate_by = 20

    def get_queryset_data(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, slug=slug)
        category_name = category.name
        self.name = category_name
        # article_list = Article.published.filter(category__name=category_name)
        article_list = {}
        return article_list

    def get_context_data(self, **kwargs):
        category_name = self.name
        kwargs['page_type'] = ArchiveView.page_type
        kwargs['tag_name'] = category_name

        category = Category.objects.get(name=category_name)
        kwargs['head_title'] = category.head_title
        kwargs['head_desc'] = category.head_desc
        kwargs['head_keywords'] = category.head_keywords
        return super(ArchiveView, self).get_context_data(**kwargs)


# class TagDetailView(ArticleListView):
#     page_type = '标签归档'
#     paginate_by = 20
#
#     def get_queryset_data(self):
#         slug = self.kwargs['tag_name']
#         tag = get_object_or_404(Tag, slug=slug)
#         tag_name = tag.name
#         self.name = tag_name
#         article_list = Article.published.filter(tags__name=tag_name, ad_property=0)
#         return article_list
#
#     def get_context_data(self, **kwargs):
#         tag_name = self.name
#         kwargs['page_type'] = TagDetailView.page_type
#         kwargs['tag_name'] = tag_name
#
#         tag = Tag.objects.get(name=tag_name)
#         kwargs['head_title'] = tag.head_title
#         kwargs['head_desc'] = tag.head_desc
#         kwargs['head_keywords'] = tag.head_keywords,
#         return super(TagDetailView, self).get_context_data(**kwargs)

