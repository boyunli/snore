from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    exclude = ('create_time', 'update_time')
    list_display = ('username', 'article', 'is_enable', 'content')
    list_editable = ['is_enable']


