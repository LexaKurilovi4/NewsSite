from bs4 import BeautifulSoup
from news.news_portal.models import News
import requests


host = "https://habr.com/"


def get_news_links():
    html = requests.get(host + "ru/news/")
    soup = BeautifulSoup(html.text, "html.parser")
    links = []
    for item in soup.find_all("article", "tm-articles-list__item"):
        links.append(item.find("a", "tm-title__link")["href"])
    return links


def get_news_body(news_link):
    #news_link = "/".join(news_link.split("/")[3::])
    html = requests.get(host + news_link)
    soup = BeautifulSoup(html.text, "html.parser")
    title = soup.find("h1", class_="tm-title tm-title_h1").span.get_text()
    body = soup.find("div", class_="article-formatted-body article-formatted-body article-formatted-body_version-2").div
    news_text = ""
    news_pictures = dict()
    author = soup.find("a", class_="tm-user-info__username").text
    i = 1
    for tag in body:
        if tag.name == "p":
            news_text += tag.text + "\n"
        if tag.name == "figure":
            news_pictures.update({str(i): {"url": tag.img["src"]}})
            news_text += "{" + str(i) + "}"
            i += 1
        if tag.name == "div":
            news_pictures.update({f"v{i}": {"url": tag["data-src"]}})
            news_text += "{v" + str(i) + "}"
            i += 1
        if tag.name =="blockquote":
            news_text += tag.p.text + "\n"
    return {
        "title": title,
        "news_text": news_text,
        "source": "Habr",
        "author_name": author,
        "category_name": "IT",
        "pictures": news_pictures
    }


def get_news_objects():
    news_links_list = get_news_links()
    news_objects_list = []
    for link in news_links_list:
        news_dict = get_news_body(link)
        news_objects_list.append(News(
            news_title=news_dict["title"],
            news_text=news_dict["news_text"],
            title_picture=news_dict["pictures"]["1"],
            pictures=news_dict["pictures"]
        ))


l = get_news_body(get_news_links()[0])
for v in l:
    print(l[v])

