from urllib import response
import scrapy 
import json
from scrapy.linkextractors import LinkExtractor
import re
import csv

class mySpider(scrapy.Spider):
    name = "product_crawler"
        
    def start_requests(self):
        yield scrapy.Request(url = "https://www.tehmart.ir/index", callback = self.parse)
        
    def parse(self, response):
        urllink_products = []
        url_lists_set = {"https://www.tehmart.ir/product/list/11/"}
        urllink_lists = []

            
        le_product = LinkExtractor()
        for link in le_product.extract_links(response):
            urllink = re.findall(r'https://www.tehmart.ir/product-[0-9]+/',link.url)
            if urllink != []:
                urllink_products.append(urllink[0])
               
        le_lists = LinkExtractor()
        for link_lists in le_lists.extract_links(response):
            urllink = re.findall(r'https://www.tehmart.ir/product/list/[0-9_]+/',link_lists.url)
            if urllink != []:
                url_lists_set.add(urllink[0])
                
        urllink_lists = list(url_lists_set)
        
               
        for url in urllink_products:
            yield scrapy.Request(url=url, callback = self.parse_product)
            
        
        for url_ls in urllink_lists:
            yield scrapy.Request(url=url_ls, callback = self.parse)
        
        
        
        
    def parse_product(self, response):
        specification_product_dict = {}
        product_about = ""   
        url = response.request.url
        row_number = int(re.findall(r'\d+', url)[0])
        title = response.xpath('//*[@id="productInfoName"]/text()').extract()[0]
        try:
            price = response.xpath('/html/body/div[1]/div[4]/div/div/div/div[1]/form/div/div[1]/div[4]/div[2]/span/span[2]/text()').extract()[0]
        except:
            price = ""
        try:
            old_price = response.xpath('/html/body/div[1]/div[4]/div/div/div/div[1]/form/div/div[1]/div[4]/div[2]/span/span[1]/text()').extract()[0]
        except:
            old_price = ""
        image_url = response.xpath('/html/body/div[1]/div[4]/div/div/div/div[1]/form/div/div[2]/div[1]/div/a/img/@src').extract()[0]
        product_about_response = response.xpath('/html/body/div[1]/div[4]/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/p').extract()
        for p in product_about_response:
            p = p.replace("<p>" , "").replace("</p>", "")
            product_about += p + "\n"
        
        specification_product_range = len(response.xpath('/html/body/div[1]/div[4]/div/div/div/div[1]/div/div/div/div[2]/div[2]/div/table/tr').extract())
        for i in range(2, specification_product_range + 1):
            specification_product_key = response.xpath(f'/html/body/div[1]/div[4]/div/div/div/div[1]/div/div/div/div[2]/div[2]/div/table/tr[{i}]/td/text()').extract()[0]
            specification_product_value = response.xpath(f'/html/body/div[1]/div[4]/div/div/div/div[1]/div/div/div/div[2]/div[2]/div/table/tr[{i}]/td/text()').extract()[1]
            specification_product_dict[specification_product_key] = specification_product_value

        specification_product = json.dumps(specification_product_dict,ensure_ascii=False)
        
        
        with open("output.txt", 'a+') as output:
            output.write(title  + "\n" + url + "\n" + price + "\n" + old_price + "\n" + image_url + "\n" + str(product_about) + "\n"+ str(specification_product))
            output.write("\n\n\n******************************\n\n\n")
        output.close()