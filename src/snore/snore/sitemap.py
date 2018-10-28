#!/usr/bin/env python
# encoding: utf-8

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from dashboard.models import Category, Tag, Article


class StaticViewSitemap(Sitemap):
    priority = 1
    changefreq = 'daily'

    def items(self):
        return ['dashboard:index', ]

    def location(self, item):
        return reverse(item)


class ArticleSiteMap(Sitemap):
    changefreq = "monthly"
    priority = "0.8"

    def items(self):
        return Article.published.all()

    def lastmod(self, obj):
        return obj.update_time


class CategorySiteMap(Sitemap):
    # changefreq = "Weekly"
    changefreq = "daily"
    priority = "0.8"

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.update_time


class TagSiteMap(Sitemap):
    changefreq = "daily"
    priority = "0.8"

    def items(self):
        return Tag.objects.all()

    def lastmod(self, obj):
        return obj.update_time


