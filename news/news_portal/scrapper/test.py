from bs4 import BeautifulSoup
import requests


host = "https://habr.com/ru/news/"


def get_news_links():
    html = requests.get(host)
    soup = BeautifulSoup(html.text, "html.parser")
    links = []
    for item in soup.find_all("article", "tm-articles-list__item"):
        links.append(item.find("a", "tm-title__link")["href"])
    return links

news_link = get_news_links()[0]
news_link = "/".join(news_link.split("/")[3::])
html = requests.get(host + news_link)
soup = BeautifulSoup(html.text, "html.parser")
title = soup.find("h1", class_="tm-title tm-title_h1").span.get_text()
datetime_string = soup.find("span", class_="tm-article-datetime-published").time["title"]

print(soup.find("div", class_="article-formatted-body article-formatted-body article-formatted-body_version-2"))