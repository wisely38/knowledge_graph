import scrapy
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse
import os.path

class FundSpider(scrapy.Spider):
    name = 'fundspider'

    def start_requests(self):
        headers = {
            "Host": "www.gbm.hsbc.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br"
        }
        urls_filepath = os.path.join("./resources/","urls.txt")
        with open(urls_filepath, mode='r') as handler:
            self.start_urls = handler.readlines()
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def found_invalid_tag(self, tag):
        tag_name = tag.name
        tags_blacklist = ['script' , 'img', 'button', 'style','link','meta']
        return tag_name in tags_blacklist     

    def should_skip_element(self, tag):
        has_invalid_child = False
        for child in tag.children:
            cleansed_tag = self.cleanse_element(child)
            if self.found_invalid_tag(child) or len(cleansed_tag)==0 or cleansed_tag== '.' or cleansed_tag== '|':
                has_invalid_child = True
                break
        return has_invalid_child

    def cleanse_element(self, tag):
        if tag is None or tag.string is None:
            return ''
        else:
            return tag.string.replace("\n","").replace(u'\xa0', u' ').strip()

    def get_sentences(self, soup):
        elements = list()
        for ele in soup.find_all(["title","div", "p", "br", "span","h5","h4","h3","h2","h1","a"]):
            if ele.find(class_='image') or self.should_skip_element(ele) or isinstance(ele.text, Comment) or ele is None:
                continue
            if ele and len(ele)>0 and str(ele.string) != "None":
                elements.append(ele.string.replace("\n", "").replace(u'\xa0', u' ').strip())
        return set(elements)       

    def parse(self, response):
        self.log("Parssing url:%s"%response.request.url)
        filename = os.path.normpath(os.path.join(os.getcwd(),"../staging", urlparse(response.request.url).path.replace("/","_") + ".txt"))
        soup = BeautifulSoup(response.body)
        sentences = self.get_sentences(soup)
        with open(filename, 'w') as handler:
            handler.writelines("%s\n" % sentence for sentence in sentences)
        self.log("File writen as %s for url:%s"%(filename,response.request.url))