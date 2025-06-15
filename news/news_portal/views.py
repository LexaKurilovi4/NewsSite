from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import *
from .test import HabrScrapper



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
        print("before query")
        context = super(SearchListView, self).get_context_data(**kwargs)
        query = self.kwargs['query'].replace('%20', ' ')
        query_re = r'(?gmiu)' + query
        news_title_match = News.objects.filter(news_title__regex=query_re)
        news_text_match = News.objects.filter(news_text__regex=query_re)
        category_match = Category.objects.filter(category_name__regex=query_re)
        news_tags_match = News.objects.filter(news_tags__regex=query_re)
        print("after query")
        category_query_set = set()
        print(category_match)
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
        for news_item in news_tags_match:
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
            category = Category.objects.get(pk=self.kwargs.get('pk'))
            context['page_obj'] = News.objects.filter(category__exact=category).order_by('-date_published')
        return context


class NewsDetailView(generic.DetailView):
    model = News
    template_name = 'news_portal/news_view.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        news = News.objects.get(pk=self.kwargs.get('pk'))
        news.news_text.replace('<', '&lt')
        for picture in news.pictures:
            news.news_text = news.news_text.replace('{' + f'{picture}' + '}', f'<img src="{news.pictures[picture]['url']}">')
        context['news'] = news
        return context


def get_tags(request):
    tags_set = Category.objects.all()
    news_list = News.objects.all()
    data = {'categories': '', 'tags': ''}
    for category in tags_set:
        data['categories'] = data['categories'] + category.category_name + ';'
    for news in news_list:
        data['tags'] = data['tags'] + news.news_tags + ',' if news.news_tags else data['tags']
    return JsonResponse(data)


def scrapp_habr_news(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("news_portal:news_list"))
    data = request.POST
    authors = []
    for author in Author.objects.all():
        authors.append(author.author_name)
    for news_object in data.get("news"):
        if news_object["author_name"] not in authors:
            author = Author(author_name=news_object["author_name"])
            author.save()
        News.objects.update_or_create(
            news_title=news_object["title"],
            title_picture=news_object["pictures"]["1"]["url"],
            news_text=news_object["news_text"],
            date_published=timezone.now(),
            source=Source.objects.filter(source_name__iexact=news_object["source"])[0],
            author=Author.objects.filter(author_name__iexact=news_object["author_name"])[0],
            pictures=news_object["pictures"],
            news_tags=news_object["tags"]
        )
    return HttpResponseRedirect(reverse("news_portal:news_list"))


if __name__ == '__main__':
    scrapp_habr_news(None)
