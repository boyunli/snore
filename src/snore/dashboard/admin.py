from django.contrib import admin
from django.utils.html import format_html

from .models import Category #, Links, Tag, SiteSettings

admin.site.site_header = '止鼾网'
admin.site.site_title = '止鼾网'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('create_time', 'update_time')
    list_display = ('id', 'name', 'is_link', 'sequence', 'icon', 'href')
    list_editable = ['is_link', 'sequence', 'icon']

    fieldsets = (
        ('base info', {'fields': ['name', 'icon', 'is_link',
                                  'link', 'sequence']}),
        ("Content", {'fields':['head_desc', 'head_title', 'head_keywords']})
    )

    def href(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">{}</a>',
                                   obj.link, obj.link)
        return obj.link
    href.short_description = '链接'

