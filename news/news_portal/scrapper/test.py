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

news_link = get_news_links()[1]
news_link = "/".join(news_link.split("/")[3::])
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
    if tag.name == "div":
        news_pictures.update({f"v{i}": {"url": tag["data-src"]}})
    i += 1
    print(tag)

#print(soup.find("a", class_="tm-user-info__username").text)

print(news_text)