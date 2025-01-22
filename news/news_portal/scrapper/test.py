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
body = soup.find("div", class_="article-formatted-body article-formatted-body article-formatted-body_version-2").div
news_text = ""
news_pictures = ""
author = soup.find("a", class_="tm-user-info__username").text
for tag in body:
    if tag.name == "p":
        news_text += tag.text + "\n"
    if tag.name == "figure":
        news_pictures += tag.img["src"] + "\n"
        news_text += "img\n"

print(soup.find("a", class_="tm-user-info__username").text)

#print(body)