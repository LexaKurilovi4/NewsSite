from django.urls import path
from . import views


app_name = 'news_portal'
urlpatterns = [
    path('', views.NewsListView.as_view(), name='news_list'),
    path('<int:pk>/', views.NewsDetailView.as_view(), name='news_view'),
    path('tags/', views.get_tags, name='tags'),
    path('search/<query>', views.SearchListView.as_view(), name='search'),
    path('category/<int:pk>', views.CategoryListView.as_view(), name='category'),
    path('news/scrapp_habr', views.scrapp_habr_news, name='scrapp_habr'),
]
