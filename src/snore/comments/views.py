from .forms import CommentForm
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect

from .models import Comment
from dashboard.models import Article

class CommentPostView(FormView):
    form_class = CommentForm
    template_name = 'dashboard/article.html'

    def get(self, request, *args, **kwargs):
        article_id = self.kwargs['article_id']

        article = Article.objects.get(pk=article_id)
        url = article.get_absolute_url()
        return HttpResponseRedirect(url + "#comments")

    def form_valid(self, form):
        """提交的数据验证合法后的逻辑"""

        article_id = self.kwargs['article_id']
        article = Article.objects.get(pk=article_id)
        comment = form.save(False)
        comment.article = article

        if form.cleaned_data['parent_comment_id']:
            parent_comment = Comment.objects.get(pk=form.cleaned_data['parent_comment_id'])
            comment.parent_comment = parent_comment

        comment.save(True)
        return HttpResponseRedirect("%s#div-comment-%d" % (article.get_absolute_url(), comment.pk))
