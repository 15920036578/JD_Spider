# -*- coding: utf-8 -*-
__author__ = 'Gobi Xu'


import scrapy
import datetime
import json
from items import Jd_phoneItem


# 商品列表页的每一页都有 60个商品，但是请求商品列表页时，只会显示 前30个商品，剩下的30个商品 是下滑商品列表页时 异步加载 出来的
# 使用抓包的方法可以截取到 剩下的30个商品的请求地址，请求地址尾部包含了 前30个商品 的 商品id，头部信息里的 Referer 为 商品列表页的请求地址
# 商品列表页 一共100页。第一页的请求地址中 page 参数为 1，第一页的 剩下30个商品的请求地址中 page 参数为 2。第二页的请求地址中 page 参数为 3，第二页的 剩下30个商品的请求地址中 page 参数为 4....以此类推
# 商品详情页 可以加载到 商品评论js页面 的请求地址


class JdPhoneSpider(scrapy.Spider):
    name = 'jd_phone'
    allowed_domains = ['jd.com']
    # 需要爬取的 类目
    keyword = '手机'
    # 商品列表页的 初始页
    page = 1
    # 商品列表页 的请求地址
    top_thirty_url = 'https://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&page=%d&click=0'
    # 商品列表页 异步加载得到的 剩下30个商品 的请求地址
    later_thirty_url = 'https://search.jd.com/s_new.php?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&page=%d&scrolling=y&tpl=3_M&show_items=%s'
    # 商品评论js页面 的请求地址
    comment_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=%s'

    # custom_settings = {}

    def start_requests(self):
        # 请求 商品列表页的第1页，获取的商品列表页只包含 前30个商品
        yield scrapy.Request(url=self.top_thirty_url%(self.keyword,self.page), callback=self.parse)

    def parse(self, response):
        # id_list用于获取 商品列表页前30个商品id
        id_list = []
        # 获取商品列表页 前30个商品的gl-item列表
        gl_items = response.css('.gl-item')
        for gl_item in gl_items:
            # 获取 商品价格
            price = float(gl_item.css('.gl-i-wrap .p-price strong i::text').extract_first(0))
            # 获取 商品详情页请求地址
            url = gl_item.css('.gl-i-wrap .p-name a::attr(href)').extract_first('')
            # 如果地址以 // 开头，将它转换成 http：//（例：//item.jd.com/5089253.html >> http：//item.jd.com/5089253.html）
            if url.startswith('//'):
                url = ''.join(['http:', url])
            # 获取 商品id 并且加入到 id_list
            id = gl_item.css('.gl-item::attr(data-pid)').extract_first('')
            id_list.append(id)
            # 回调到 处理 商品评论js页面 的函数
            yield scrapy.Request(url=self.comment_url%(id), callback=self.parseComment, meta={'price':price,'url':url})
        if self.page <= 199:
            self.page += 1
            id_list = ','.join(id_list)
            # 回调到 处理 商品列表页剩下30个商品 的函数
            yield scrapy.Request(url=self.later_thirty_url%(self.keyword,self.page,id_list), callback=self.parseNext, headers={'Referer':response.url})

    def parseNext(self, response):
        # 处理方式和 parse函数 基本无差别
        gl_items = response.css('.gl-item')
        for gl_item in gl_items:
            price = float(gl_item.css('.gl-i-wrap .p-price strong i::text').extract_first(0))
            url = gl_item.css('.gl-i-wrap .p-name a::attr(href)').extract_first('')
            if url.startswith('//'):
                url = ''.join(['http:', url])
            id = gl_item.css('.gl-item::attr(data-pid)').extract_first('')
            yield scrapy.Request(url=self.comment_url%(id), callback=self.parseComment, meta={'price':price,'url':url})
        if self.page <= 199:
            self.page += 1
            # 回调到 处理 下一页商品列表页 的函数
            yield scrapy.Request(url=self.top_thirty_url%(self.keyword,self.page), callback=self.parse)

    def parseComment(self, response):
        comment_dict = json.loads(response.text)['CommentsCount'][0]
        # 获取 商品总评论数
        comment_count = comment_dict.get('CommentCount', 0)
        # 获取 商品好评数
        good_count = comment_dict.get('GoodCount', 0)
        # 获取 商品中评数
        general_count = comment_dict.get('GeneralCount', 0)
        # 获取 商品差评数
        poor_count = comment_dict.get('PoorCount', 0)
        # 获取 商品被展示次数
        show_count = comment_dict.get('ShowCount', 0)
        # 获取 商品id
        id = comment_dict.get('SkuId', 0)
        # 回调到 处理 商品详情页 的函数
        yield scrapy.Request(url=response.meta['url'], callback=self.parseDetail, meta={'price':response.meta['price'],'comment_count':comment_count,'good_count':good_count,'general_count':general_count,'poor_count':poor_count,'show_count':show_count,'id':id})

    def parseDetail(self, response):
        # 获取 商品标题
        title = response.css('#spec-img::attr(alt)').extract_first('')
        # 获取 商品品牌
        brand = response.css('.inner.border .head a::text').extract_first('')
        if not brand:
            brand = response.css('#parameter-brand li::attr(title)').extract_first('')
        # 获取 商品型号
        model = response.css('.item.ellipsis::text').extract_first('')
        if not model:
            model = response.css('.parameter2.p-parameter-list li::attr(title)').extract_first('')
        # 获取 商品的店名
        shop_name = response.css('.J-hove-wrap.EDropdown.fr .item .name a::text').extract_first('')
        if not shop_name:
            shop_name = response.css('.item.hide.J-im-item .J-im-btn .im.customer-service::attr(data-seller)').extract_first('')
        # 获取 商品url
        url = response.url
        # 获取 当前时间
        crawl_date = datetime.datetime.now()
        # 获取 meta中的值
        price = response.meta['price']
        id = response.meta['id']
        comment_count = response.meta['comment_count']
        good_count = response.meta['good_count']
        general_count = response.meta['general_count']
        poor_count = response.meta['poor_count']
        show_count = response.meta['show_count']
        # 传入 item
        item = Jd_phoneItem()
        item['id'] = id
        item['title'] = title
        item['url'] = url
        item['shop_name'] = shop_name
        item['price'] = price
        item['brand'] = brand
        item['model'] = model
        item['comment_count'] = comment_count
        item['good_count'] = good_count
        item['general_count'] = general_count
        item['poor_count'] = poor_count
        item['show_count'] = show_count
        item['crawl_date'] = crawl_date
        yield item
