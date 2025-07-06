import scrapy
from ..items import MerchantItem


class SpiderMerchantpointSpider(scrapy.Spider):
    name = "spider_merchantpoint"
    allowed_domains = ["merchantpoint.ru"]
    start_urls = ["https://merchantpoint.ru/brands"]

    def parse(self, response):
        for href_brand in response.xpath('//table//tr/td/a[contains(@href, "/brand/")]/@href').getall():
            yield scrapy.Request(response.urljoin(href_brand), callback=self.parse_brand)

        next_page = response.xpath('//a[contains(text(), "Далее")]/@href').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_brand(self, response):
        org_name = response.xpath('//h1/text()').get().strip()
        org_description = ' '.join(response.xpath('//div[contains(@class, "description")]//text()').getall()).strip()
        
        for href_point in response.xpath('//tbody/tr/td/a/@href').getall():
            yield scrapy.Request(
                response.urljoin(href_point),
                callback=self.parse_point,
                meta={'org_name': org_name, 'org_description': org_description}
            )

    def parse_point(self, response):
        def get_text(xpath):
            text = response.xpath(xpath).get('').strip()
            return text.lstrip('— ').strip() if text else ''

        item = MerchantItem()
        item['merchant_name'] = get_text('//b[contains(text(), "MerchantName")]/following-sibling::text()')
        item['mcc'] = get_text('//b[contains(text(), "MCC")]/following-sibling::a/text()')
        item['address'] = get_text('//b[contains(text(), "Адрес")]/following-sibling::text()')
        item['geo_coordinates'] = get_text('//b[contains(text(), "Геокоординаты")]/following-sibling::text()')
        item['org_name'] = response.meta.get('org_name', '')
        item['org_description'] = response.meta.get('org_description', '')
        item['source_url'] = response.url
        
        yield item
