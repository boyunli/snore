import os
import re

from PIL import Image as Img
from django.contrib import admin
from django.utils.html import format_html

from snore.settings import MEDIA_ROOT
from .models import Category, Article, Tag, Link, SiteSettings

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


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    exclude = ('create_time', 'update_time')
    list_display = ('title', 'category', 'ad_property',
                    'is_product', 'link', 'is_published', 'preview')
    list_editable = ['ad_property', 'is_published']

    fieldsets = (
        ('base info', {'fields': ['title', 'category', 'ad_image',
                                  'image', 'ad_property',
                                  'is_broadcast', 'is_product',
                                  'link']}),
        ("Content", {'fields':['content', 'tags']})
    )
    filter_horizontal=('tags',)

    def save_model(self, request, obj, form, change):
        # import pdb;pdb.set_trace()
        if 'content' in form.changed_data:
            images = re.findall(r'src="(.*?)"', obj.content)
            for image in images:
                image_path = os.path.join(MEDIA_ROOT, image.split('/media/')[1])
                thumb = '_thumb.'.join(image_path.split('.'))
                if not os.path.exists(thumb):
                    # 不进行重复 crop
                    continue
                else:
                    img = Img.open(image_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    os.remove(thumb)
                    img.thumbnail((img.width/1.5, img.height/1.5), Img.ANTIALIAS)
                    img.save(image_path, format='JPEG', optimize=True, quality=70)
        super(ArticleAdmin, self).save_model(request, obj, form, change)

    def preview(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>',
                               obj.get_absolute_url(), obj.pk)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    exclude = ('create_time', 'update_time')
    list_display = ('id', 'name', 'slug')


@admin.register(Link)
class LinksAdmin(admin.ModelAdmin):
    exclude = ('slug', 'create_time', 'update_time')
    list_display = ('name', 'url')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('sitename', 'filing_number')

    def has_delete_permission(self, request, obj=None):
        '''
        禁止admin 删除
        '''
        return False

