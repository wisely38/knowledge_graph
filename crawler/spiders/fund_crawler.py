import scrapy
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse
import os.path
import shutil
from datetime import date
from random_useragent.random_useragent import Randomize
import requests

class FundSpider(scrapy.Spider):
    name = 'fundspider'

    def start_requests(self):
        r_agent = Randomize()
        firstrequest_headers = {
            "X-FORWARDED-FOR": "2.16.167.33",
            "Host": "www.assetmanagement.hsbc.co.uk",
            "User-Agent": r_agent.random_agent('desktop','windows'),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br"
        }
        firsturl = "https://hsbcbankglobal.sc.omtrdc.net/b/ss/hsbc-amg-uk,hsbc-amg-global-rollup/1/JS-2.0.0/s78194187988030?AQB=1&ndh=1&pf=1&t=7%2F10%2F2019%2011%3A45%3A31%204%20-480&sdid=5D631A30BB0D4398-0DF62F7812D9139F&mid=64095394369463805659018752405389641208&ce=UTF-8&ns=hsbcbankglobal&pageName=Global%20High%20Income%20Bond%20-%20HSBC%20Global%20Asset%20Management%20UK&g=https%3A%2F%2Fwww.assetmanagement.hsbc.co.uk%2Fen%2Fintermediary%2Finvestment-expertise%2Ffixed-income%2Fglobal-high-income-bond&cc=USD&server=www.assetmanagement.hsbc.co.uk&events=event27&v1=Global%20High%20Income%20Bond%20-%20HSBC%20Global%20Asset%20Management%20UK&v2=High%20Income%20Bond%20-%20HSBC%20Global%20Asset%20Management%20UK&v3=www.assetmanagement.hsbc.co.uk%2Fen%2Fintermediary%2Finvestment-expertise%2Ffixed-income%2Fglobal-high-income-bond&c6=hsbc-amg-uk%2Chsbc-amg-global-rollup&c7=11%3A45%20AM%7CThursday&c13=accept&v15=11%3A45%20AM%7CThursday&v16=hsbc-amg-uk%2Chsbc-amg-global-rollup&c17=uk-gam&v17=uk-gam&v96=content&v98=Terms%20and%20conditions&v99=accept&pe=lnk_o&pev2=no%20link_name&pid=Intermediary%20%7C%20Investment%20Expertise%20%7C%20Fixed%20Income%20%7C%20Global%20High%20Income%20Bond&pidt=1&oid=https%3A%2F%2Fwww.assetmanagement.hsbc.co.uk%2Fen%2Fintermediary%2Finvestment-expertise%2Ffixed-income%2Fglobal-high&ot=A&s=1920x1080&c=24&j=1.6&v=N&k=Y&bw=1835&bh=634&AQE=1"
        response = requests.get(firsturl, headers=firstrequest_headers)
        self.log("Http code,reason:%s,%s" % (response.status_code, response.reason))
        referer = response.request.headers.get('Referer', None)
        headers = firstrequest_headers.setdefault("Referer",referer)
        self.log("headers:%s"%headers)
        urls_filepath = os.path.join("./resources/","urls.txt")
        with open(urls_filepath, mode='r') as handler:
            self.start_urls = handler.readlines()

        self.subfoldername = "../staging" + "/" + date.today().strftime("%m-%d-%Y") 
        subfolderpath = os.path.normpath(os.path.join(os.getcwd(), self.subfoldername))
        self.log("subfolderpath:%s"%type(subfolderpath))
        if os.path.exists(subfolderpath):
            # os.rmdir(subfolderpath)
            shutil.rmtree(subfolderpath, ignore_errors=True)
        os.mkdir(subfolderpath)

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
        for ele in soup.find_all(["title","div", "p", "br", "span","h5","h4","h3","h2","h1","a","li"]):
            if ele.find(class_='image') or self.should_skip_element(ele) or isinstance(ele.text, Comment) or ele is None:
                continue
            if ele and len(ele)>0 and str(ele.string) != "None":
                elements.append(ele.string.replace("<strong>","").replace("</strong>","").replace("\n", "").replace(u'\xa0', u' ').strip())
        return set(elements)       

    def parse(self, response):
        self.log("Parssing url:%s"%response.request.url)
        filename = "crawler-output" + urlparse(response.request.url).path.replace("/","_") + ".txt"
        filepath = os.path.normpath(os.path.join(os.getcwd(), self.subfoldername, filename))
        soup = BeautifulSoup(response.body)
        sentences = self.get_sentences(soup)
        with open(filepath, 'w') as handler:
            handler.writelines("%s\n" % sentence for sentence in sentences)
        self.log("File writen as %s for url:%s"%(filename,response.request.url))