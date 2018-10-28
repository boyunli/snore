from django.db import models

from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from dashboard.models import Article


class Comment(models.Model):
    BOOLEAN_CHOICES = (
        (True, '是'),
        (False, '否'),
    )

    article = models.ForeignKey(Article, verbose_name='文章', on_delete=models.CASCADE)
    username = models.CharField(_('用户'), max_length=20)
    qq = models.CharField(_('QQ'), max_length=20)
    parent_comment = models.ForeignKey('self', verbose_name="上级评论", blank=True, null=True, on_delete=models.CASCADE)
    content = models.TextField(_('正文'), max_length=500)
    is_enable = models.BooleanField(_('是否显示'), default=False, choices=BOOLEAN_CHOICES)
    create_time = models.DateTimeField(_('创建时间'), default=now)
    update_time = models.DateTimeField(_('更新时间'), default=now)

    class Meta:
        ordering = ['-create_time']
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        get_latest_by = 'create_time'

    def __str__(self):
        return self.content
