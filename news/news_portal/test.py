from bs4 import BeautifulSoup
import requests


class HabrScrapper:
    def __init__(self):
        self.host = "https://habr.com/"
        self.news_links = self.get_news_links()

    def get_news_links(self):
        html = requests.get(self.host + "ru/news/")
        soup = BeautifulSoup(html.text, "html.parser")
        links = []
        for item in soup.find_all("article", "tm-articles-list__item"):
            links.append(item.find("a", "tm-title__link")["href"])
        return links

    def get_news_body(self, news_link):
        html = requests.get(self.host + news_link)
        soup = BeautifulSoup(html.text, "html.parser")
        title = soup.find("h1", class_="tm-title tm-title_h1").span.get_text()
        body = soup.find("div",
                         class_="article-formatted-body article-formatted-body article-formatted-body_version-2").div
        news_text = ""
        news_pictures = dict()
        author = soup.find("a", class_="tm-user-info__username").text
        tags_container = soup.find("div", class_="tm-publication-hubs__container").div
        tags = ""
        for tag in tags_container:
            if tag == "[" or tag == "]":
                continue
            tags += tag.a.span.get_text() + ","
        i = 1
        for tag in body:
            if tag.name == "p":
                news_text += tag.text + "\n"
            if tag.name == "figure":
                news_pictures.update({str(i): {"url": tag.img.get("data-src", tag.img["src"])}})
                news_text += "{" + str(i) + "}"
                i += 1
            if tag.name == "div":
                try:
                    news_pictures.update({f"v{i}": {"url": tag["data-src"]}})
                    news_text += "{v" + str(i) + "}"
                    i += 1
                except Exception:
                    break
            if tag.name == "blockquote":
                news_text += tag.p.text + "\n"
        if news_pictures == {}:
            news_pictures.update({"1": {"url": "https://www.svgrepo.com/show/418518/brain-brainstorm-creative.svg"}})
        return {
            "id": news_link.split("/")[-2],
            "title": title,
            "news_text": news_text,
            "source": "Habr",
            "author_name": author,
            "category_name": "IT",
            "pictures": news_pictures,
            "tags": tags
        }


if __name__ == "__main__":
    scrapper = HabrScrapper()
    for link in scrapper.news_links:
        print(link)
        scrapper.get_news_body(link)
        print("-" * 20)
