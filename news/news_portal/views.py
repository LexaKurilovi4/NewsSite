import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils import timezone
from .models import *
from scrapper.test import HabrScrapper


class NewsListView(generic.ListView):
    model = News
    template_name = 'news_portal/news_list.html'
    context_object_name = 'page_obj'

    def get_queryset(self):
        return News.objects.filter(
            date_published__lte=timezone.now()).order_by('-date_published')[:10]

    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class SearchListView(generic.ListView):
    model = News
    template_name = 'news_portal/search_results.html'
    context_object_name = 'page_obj'

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        query = self.kwargs['query'].replace('%20', ' ')
        news_title_match = News.objects.filter(news_title__icontains=query)
        news_text_match = News.objects.filter(news_text__icontains=query)
        category_match = Category.objects.filter(category_name__icontains=query)
        category_query_set = set()
        for category in category_match:
            news = News.objects.filter(category__exact=category)
            category_query_set.update(news)
        query_dict = dict()
        for news_item in news_title_match:
            query_dict.update({news_item: 1})
        for news_item in news_text_match:
            if news_item in query_dict:
                query_dict.update({news_item: query_dict.get(news_item) + 1})
            else:
                query_dict.update({news_item: 1})
        for news_item in category_query_set:
            if news_item in query_dict:
                query_dict.update({news_item: query_dict.get(news_item) + 1})
            else:
                query_dict.update({news_item: 1})
        sorted_dict = {k: v for k, v in sorted(query_dict.items(), key=lambda item: item[1], reverse=True)}
        context['page_obj'] = sorted_dict
        return context


class CategoryListView(generic.ListView):
    model = News
    template_name = 'news_portal/search_results.html'
    context_object_name = 'page_obj'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        if self.kwargs.get('pk') == 0:
            context['page_obj'] = News.objects.all().order_by('-date_published')
        else:
            category = Category.objects.get(pk=self.kwargs.get('pk')).order_by('-date_published')
            context['page_obj'] = News.objects.filter(category__exact=category)
        return context


class NewsDetailView(generic.DetailView):
    model = News
    template_name = 'news_portal/news_view.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        news = News.objects.get(pk=self.kwargs.get('pk'))
        for picture in news.pictures:
            news.news_text = news.news_text.replace('{' + f'{picture}' + '}', f'<img src="{news.pictures[picture]['url']}" width={news.pictures[picture]['width']}>')
        context['news'] = news
        return context


def get_tags(request):
    tags_set = Category.objects.all()
    data = {'categories': '', 'tags': ''}
    for category in tags_set:
        data['categories'] = data['categories'] + category.category_name + ';'
    return JsonResponse(data)


def scrapp_habr_news():
    scrapper = HabrScrapper()
    f = open("scrapper/habr.txt", "r")
    last_link = f.readline()
    f.close()
    with open("scrapper/habr.txt", "w") as file:
        file.write(scrapper.news_links[0])
    if last_link in scrapper.news_links:
        scrapper.news_links = scrapper.news_links[:scrapper.index(last_link)]
    news = []
    authors = []
    for author in Author.objects.all():
        authors.append(author.author_name)
    for link in scrapper.news_links:
        news_object = scrapper.get_news_body(link)
        if news_object["author_name"] not in authors:
            author = Author(author_name=news_object["author_name"])
            author.save()
        news.append(News(
            news_title=news_object["title"],
            news_text=news_object["text"],
            date_published=timezone.now(),
            source=Source.objects.filter(source_name__iexact=news_object["source"]),
            author=Author.objects.filter(author_name__iexact=news_object["author_name"]),
            category=Category.objects.filter(category_name__iexact=news_object["category_name"]),
            pictures=news_object["pictures"]
        ))

