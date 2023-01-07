import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re
import requests
class med_data():
    def __init__(self):
        print("___init_____")
        self.conn = pymongo.MongoClient()
        self.db = self.conn['medical']
        self.col = self.db['data2']
    def get_html(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        res= requests.get(url,headers=headers)
        html=res.content
        
        return html
    def main_spider(self):
        root_url="http://jib.xywy.com/il_sii/"
        for i in range(1,11000):
            gaishu_url=root_url+"gaishu/{}.htm".format(i)
            cause_url=root_url+"cause/{}.htm".format(i)
            prevent_url=root_url+"prevent/{}.htm".format(i)
            symptom_url=root_url+"symptom/{}.htm".format(i)
            inspect_url=root_url+"inspect/{}.htm".format(i)
            treat_url=root_url+"treat/{}.htm".format(i)
            food_url=root_url+"food/{}.htm".format(i)
            drug_url=root_url+"drug/{}.htm".format(i)
            data = {}
            data['url'] = root_url
            data['gaishu'] = self.gai_spider(gaishu_url)
            data['cause'] =  self.cas_pre_spider(cause_url)
            data['prevent'] =  self.cas_pre_spider(prevent_url)
            data['symptom'] = self.symptom_spider(symptom_url)
            data['inspect'] = self.inspect_spider(inspect_url)
            data['treat'] = self.treat_spider(treat_url)
            data['food'] = self.food_spider(food_url)
            data['drug'] = self.drug_spider(drug_url)
            print(i, gaishu_url)
            self.col.insert_one(data)

    def gai_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')[0]
        category = selector.xpath('//div[@class="wrap mt10 nav-bar"]/a/text()')
        desc = selector.xpath('//div[@class="jib-articl-con jib-lh-articl"]/p/text()')
        ps = selector.xpath('//div[@class="mt20 articl-know"]/p')
        infos = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            infos.append(info)
        gaishu = {}
        gaishu['category'] = category
        gaishu['name'] = title.split('的简介')[0]
        gaishu['desc'] = desc
        gaishu['attributes'] = infos
        return gaishu

    def treat_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//div[starts-with(@class,"mt20 articl-know")]/p')
        infos = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            infos.append(info)
        return infos

    def drug_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        drugs = [i.replace('\n','').replace('\t', '').replace(' ','') for i in selector.xpath('//div[@class="fl drug-pic-rec mr30"]/p/a/text()')]
        return drugs

    def food_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        divs = selector.xpath('//div[@class="diet-img clearfix mt20"]')
        try:
            food_data = {}
            food_data['good'] = divs[0].xpath('./div/p/text()')
            food_data['bad'] = divs[1].xpath('./div/p/text()')
            food_data['recommand'] = divs[2].xpath('./div/p/text()')
        except:
            return {}
        return food_data

    def symptom_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        symptoms = selector.xpath('//a[@class="gre" ]/text()')
        ps = selector.xpath('//p')
        detail = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0', '').replace('   ', '').replace('\t','')
            detail.append(info)
        symptoms_data = {}
        symptoms_data['symptoms'] = symptoms
        symptoms_data['symptoms_detail'] = detail
        return symptoms, detail
    
    def inspect_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        inspects  = selector.xpath('//li[@class="check-item"]/a/@href')
        return inspects

    def cas_pre_spider(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        ps = selector.xpath('//p')
        infos = []
        for p in ps:
            info = p.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ','').replace('\t', '')
            if info:
                infos.append(info)
        return '\n'.join(infos)

    def inspect_crawl(self):
        for i in range(690, 3685):
            try:
                url = 'http://jck.xywy.com/jc_%s.html'.format(i)
                html = self.get_html(url)
                data = {}
                data['url']= url
                data['html'] = html
                self.db['jc'].insert_one(data)
                print(url)
            except Exception as e:
                print(e)
med=med_data()
med.main_spider()
med.inspect_crawl()
        
