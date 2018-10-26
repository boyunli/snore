import os
import datetime
from io import BytesIO

from PIL import ImageOps, Image as Img


from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from uuslug import slugify

from ckeditor_uploader.fields import RichTextUploadingField
from snore.settings import MEDIA_ROOT

import logging
logger = logging.getLogger('snore')


class BaseModel(models.Model):
    slug = models.SlugField(default='no-slug', max_length=160, blank=True)
    create_time = models.DateTimeField(_('创建时间'), default=timezone.now)
    update_time = models.DateTimeField(_('更新时间'), default=timezone.now)
    head_title = models.TextField(_('HeadTitle'), blank=False)
    head_desc = models.TextField(_('HeadDesc'), blank=False)
    head_keywords = models.TextField(_('HeadKeywords'), blank=False)

    def get_full_url(self):
        site = Site.objects.get_current().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == 'no-slug' or not self.id:
            slug = self.title if 'title' in self.__dict__ else self.name
            self.slug = slugify(slug)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Category(BaseModel):
    '''
    首页主要板块: 根据货源类别
    '''
    LINK_CHOICES = (
        (False, '否'),
        (True, '是'),
    )

    NEWS = '打鼾产品'
    ACADEMY = '打鼾2'
    CHUANGYE = '打鼾3'
    CATEGORY_CHOICES = (
        (NEWS, NEWS),
        (ACADEMY, ACADEMY),
        (CHUANGYE, CHUANGYE),
    )
    name = models.CharField(_('类别'), choices=CATEGORY_CHOICES, default=NEWS,
                                max_length=20, unique=True)
    sequence = models.IntegerField(_('排序'), unique=True, help_text=_('数字从小到大排列分类位置.'))
    is_link = models.BooleanField(_('是否外链'), choices=LINK_CHOICES, default=False)
    link = models.URLField(_('链接'), help_text=_('若设置外链，请提供链接!'), null=True, blank=True)
    icon = models.CharField(_('图标'), max_length=20)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        ordering = ['sequence']
        db_table = 'dashboard_category'
        verbose_name = verbose_name_plural = _('类别')

    def get_absolute_url(self):
        return reverse('dashboard:category', kwargs={'category': self.slug})

    def clean(self):
        if self.is_link and not self.link:
            raise ValidationError('If is_link is True, Must provide links!')
        super(Category, self).clean()


class Tag(BaseModel):
    """文章标签"""
    name = models.CharField('标签名', max_length=30, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dashboard:tag', kwargs={'tag': self.slug})

    # @cache_decorator(60 * 60 * 10)
    # def get_article_count(self):
    #     return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        db_table = 'dashboard_tag'
        verbose_name = "热门标签"
        verbose_name_plural = verbose_name


class PublishedManager(models.Manager):

    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(is_published=True)


class Article(models.Model):
    '''
    产品
    '''
    BOOLEAN_CHOICES = (
        (False, '否'),
        (True, '是'),
    )

    POSITION0 = 0
    POSITION1 = 1
    POSITION2 = 2
    POSITION3 = 3
    POSITION4 = 4
    POSITION5 = 5
    POSITION_CHOICES = (
        (POSITION0, '非广告'),
        (POSITION1, '首页轮播广告'),
        (POSITION2, '首页广告栏'),
        (POSITION3, '分类页广告栏'),
        (POSITION4, '优质推荐'),
        (POSITION5, '文章页广告'),
    )
    title = models.CharField(max_length=150, verbose_name='标题', unique=True)
    category = models.ForeignKey(Category, verbose_name='类别', on_delete=models.CASCADE)
    content = RichTextUploadingField(_('内容'), config_name='default', null=True, blank=True)
    ad_image = models.ImageField(_('广告图'),
                              help_text=(_('注：广告轮播图尺寸为:宽800*长300; 普通广告图尺寸为：宽280*长210')),
                              upload_to=datetime.datetime.now().strftime('article/ad/%Y/%m/%d'), null=True, blank=True)
    image = models.ImageField(_('首图'),
                              upload_to=datetime.datetime.now().strftime('article/%Y/%m/%d'), null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)
    views = models.PositiveIntegerField(_('阅读量'), default=0)
    ad_property = models.IntegerField(_('广告属性'), choices=POSITION_CHOICES, default=POSITION0)
    link = models.URLField(_('外链'), help_text=_('若设置了产品页，请提供链接!'), null=True, blank=True)
    create_time = models.DateTimeField(_('创建时间'), default=timezone.now)
    update_time = models.DateTimeField(_('更新时间'), default=timezone.now)

    is_broadcast = models.BooleanField(_('是否广播'), choices=BOOLEAN_CHOICES, default=False)
    is_product = models.BooleanField(_('Is Product'), choices=BOOLEAN_CHOICES, default=False)
    is_published = models.BooleanField(_('是否发布'), choices=BOOLEAN_CHOICES, default=False)

    objects = models.Manager()
    published = PublishedManager()
    __original_image = None
    __original_ad_image = None

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        ordering = ['-update_time']
        db_table = 'dashboard_article'
        verbose_name = verbose_name_plural = '文章'


    def clean(self):
        if self.is_product and not self.link:
            raise ValidationError('If is_product is True, Must provide link!')
        super(Article, self).clean()

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)
        self.__original_image = self.image
        self.__original_ad_image = self.ad_image

    def image_url(self):
        if self.ad_image:
            return self.ad_image.url
        else:
            return self.image.url

    def get_absolute_url(self):
        return reverse('dashboard:article', kwargs={
            'article_id': self.id,
        })

    def viewed(self):
        '''
        增加阅读数
        '''
        self.views +=1
        # update_fields 只更新数据库中的views
        self.save(update_fields=['views'], is_update_views=True)

    # # def comment_list(self):
    # #     cache_key = 'article_comments_{id}'.format(id=self.id)
    # #     value = cache.get(cache_key)
    # #     if value:
    # #         return value
    # #     else:
    # #         comments = self.comment_set.filter(is_enable=True)
    # #         cache.set(cache_key, comments)
    # #     return comments

    # @property
    # def first_para(self):
    #     return re.sub('[\r\s\t\n]', '', self.content[:100])

    # @property
    # def comment_count(self):
    #     return self.comment_set.all().count()

    def _resize_img(self, image, is_ad=False):
        image_path = BytesIO(image.read())
        img = Img.open(image_path)
        if is_ad:
            # 除了大的轮播广告图片为800*300， 其他分类展示图片大小为 宽/长 = 280/210
            if self.ad_property == self.POSITION1:
                img = ImageOps.fit(img, (800,300), Img.ANTIALIAS)
            elif self.ad_property in (self.POSITION2, self.POSITION3):
                img = ImageOps.fit(img, (728,90), Img.ANTIALIAS)
            else:
                img = ImageOps.fit(img, (280,210), Img.ANTIALIAS)
            output= BytesIO()
            img.save(output, format='JPEG', optimize=True, quality=70)
            self.ad_image= InMemoryUploadedFile(output, 'ImageField', image.name,
                                             'image/jpeg', output.getbuffer().nbytes, None)
        else:
            img = ImageOps.fit(img, (280,210), Img.ANTIALIAS)
            output= BytesIO()
            img.save(output, format='JPEG', optimize=True, quality=70)
            self.image= InMemoryUploadedFile(output, 'ImageField', image.name,
                                             'image/jpeg', output.getbuffer().nbytes, None)
            # 因为重写图片时会重新生成一张图片，所以删除原图以节约磁盘
            image_path = os.path.join(MEDIA_ROOT, image.name)
            if os.path.exists(image_path):
                os.remove(image_path)

    def save(self, is_update_views=False, *args,  **kwargs):
        # import pdb;pdb.set_trace()
        if not is_update_views:
            if self.ad_image and self.ad_image != self.__original_ad_image:
                self._resize_img(self.ad_image, is_ad=True)
                self.__original_ad_image = self.ad_image
            if self.image and self.image != self.__original_image:
                self._resize_img(self.image)
                self.__original_image = self.image
        super(Article, self).save(*args, **kwargs)



class Link(BaseModel):
    '''
    友情链接
    '''
    name = models.CharField(_('站点'), max_length=15)
    url = models.URLField(_('URL'), max_length=300)
    sequence = models.IntegerField(_('排序'), unique=True, help_text=_('数字从小到大排列标签位置.'))

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        ordering = ['sequence']
        db_table = 'dashboard_link'
        verbose_name = verbose_name_plural = _('友情链接')



#
# class SiteSettings(models.Model):
#     '''
#     站点设置
#     '''
#     sitename = models.CharField("网站名称", max_length=100, null=False, blank=False, default='')
#     head_title = models.TextField("首页标题", max_length=1000, null=False, blank=False, default='')
#     head_desc = models.TextField("首页描述", max_length=1000, null=False, blank=False, default='')
#     head_keywords = models.TextField("首页关键字", max_length=1000, null=False, blank=False, default='')
#     article_sub_length = models.IntegerField("文章摘要长度", default=300)
#     sidebar_flow_info_count = models.IntegerField("侧边栏信息流数目", default=10)
#     sidebar_recomm_count = models.IntegerField("侧边栏推荐帖文数目", default=5)
#
#     qq_bar_code = models.ImageField(_('QQ二维码'), upload_to='site/qq')
#     qq = models.CharField(_("QQ"), max_length=20)
#
#     wechat_pay_code = models.ImageField(_('微信支付维码'), upload_to='site/wechat')
#     alipay_code = models.ImageField(_('支付宝二维码'), upload_to='site/alipay')
#     phone = models.CharField('手机', max_length=11)
#
#     beiancode = models.CharField('备案号', max_length=2000, null=True, blank=True, default='')
#     analyticscode = models.TextField("网站统计代码", max_length=1000, null=False, blank=False, default='')
#     show_gongan_code = models.BooleanField('是否显示公安备案号', default=False, null=False)
#     gongan_beiancode = models.TextField('公安备案号', max_length=2000, null=True, blank=True, default='')
#
#     class Meta:
#         db_table = 'dashboard_settings'
#         verbose_name = '网站配置'
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.sitename
#
#     def clean(self):
#         if SiteSettings.objects.exclude(id=self.id).count():
#             raise ValidationError(_('只能有一个配置'))
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         from weishangdl.utils import cache
#         cache.clear()
