import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hebbank.items import Article


class hebbankSpider(scrapy.Spider):
    name = 'hebbank'
    start_urls = ['http://www.hebbank.com/hbbank/xwzx/303536/index.html']

    def parse(self, response):
        articles = response.xpath('//table[@class="liebiao"]//tr')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('.//td[@class="date121"]/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[text()="下一页"]/@tagname').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//table[@class="normal"]//tr[1]//text()').getall()
        title = [text.strip() for text in title if text.strip() and '{' not in text]
        title = " ".join(title).strip()

        content = response.xpath('//table[@class="normal"]//tr[3]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
