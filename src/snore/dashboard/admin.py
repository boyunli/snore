import os
import re

from PIL import Image as Img
from django.contrib import admin
from django.utils.html import format_html

from snore.settings import MEDIA_ROOT
from snore.utils import add_watermark
from .models import Category, Article, Tag, Link, SiteSettings
from .views import settings

admin.site.site_header = settings.sitename
admin.site.site_title = settings.sitename


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('create_time', 'update_time')
    list_display = ('name', 'slug', 'is_link', 'sequence', 'icon', 'href')
    list_editable = ['is_link', 'sequence', 'icon']

    fieldsets = (
        ('base info', {'fields': ['name', 'slug', 'icon', 'is_link',
                                  'link', 'sequence']}),
        ("Content", {'fields': ['head_title', 'head_desc', 'head_keywords']})
    )

    def href(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">{}</a>',
                               obj.link, obj.link)
        return obj.link
    href.short_description = '链接'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'stitle', 'category', 'ad_property',
                    'is_published', 'update_time')
    list_editable = ['ad_property', 'is_published']
    list_filter = ('is_published', 'ad_property', 'update_time', 'category',
                   'is_product', 'is_broadcast')
    search_fields = ('title',)
    list_per_page = 20

    exclude = ('create_time', 'update_time')
    fieldsets = (
        ('base info', {'fields': ['title', 'category',
                                  'image', 'ad_property',
                                  'is_home_display', 'is_broadcast']}),
        ("Content", {'fields': ['content', 'tags']})
    )
    filter_horizontal = ('tags',)

    def stitle(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>',
                               obj.get_absolute_url(), obj.title)
    stitle.short_description = '标题'

    def save_model(self, request, obj, form, change):
        # import pdb;pdb.set_trace()
        if 'content' in form.changed_data:
            images = re.findall(r'src="(.*?)"', obj.content)
            for image in images:
                try:
                    image_path = os.path.join(MEDIA_ROOT, image.split('/media/')[1])
                except IndexError:
                    continue
                thumb = '_thumb.'.join(image_path.split('.'))
                if os.path.exists(thumb):
                    os.remove(thumb)
                    if os.path.getsize(image_path) > 300*1024:
                        img = Img.open(image_path)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.thumbnail((img.width/1.5, img.height/1.5), Img.ANTIALIAS)
                        img.save(image_path, format='JPEG', optimize=True, quality=70)
                    add_watermark(image_path, image_path)
                else:
                    # 不进行重复 crop
                    continue
        super(ArticleAdmin, self).save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    exclude = ('create_time', 'update_time')
    list_display = ('name', 'slug')
    list_per_page = 20

    fieldsets = (
        ('base info', {'fields': ['name', 'slug']}),
        ("Content", {'fields': ['head_title', 'head_desc', 'head_keywords',
                                'title', 'intro']})
    )


@admin.register(Link)
class LinksAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sequence')
    list_editable = ['sequence']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('sitename', 'filing_number')

    def has_delete_permission(self, request, obj=None):
        '''
        禁止admin 删除
        '''
        return False

