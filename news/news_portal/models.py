from django.db import models
from django.utils import timezone


class Source(models.Model):
    source_name = models.CharField(max_length=120)
    source_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.source_name


class Author(models.Model):
    author_name = models.CharField(max_length=200)

    def __str__(self):
        return self.author_name


class Category(models.Model):
    category_name = models.CharField(max_length=200)

    def __str__(self):
        return self.category_name


class News(models.Model):
    news_title = models.CharField(max_length=200)
    news_text = models.TextField()
    date_published = models.DateTimeField(default=timezone.now())
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    category = models.ManyToManyField(Category)
    title_picture = models.URLField()
    pictures = models.JSONField()
    news_tags = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.news_title

