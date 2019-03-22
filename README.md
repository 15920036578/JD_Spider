# 京东爬虫
![](https://img.shields.io/badge/Python-3.5.3-green.svg)
#### 京东官网 - https://www.jd.com
|Author|Gobi Xu|
|---|---|
|Email|792799564@qq.com|
****
## 声明
#### 任何内容都仅用于学习交流，请勿用于任何商业用途。
## 介绍
> **目前只有爬取[手机](https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=&pvid=e7b33af1d11d4f70b6d8bdfb8fc7be87)这个类目**
- **对应的类目在items.py里**
- **对应的爬虫在spiders/jd_xxxx.py里**
> **对应的spider里有详细过程注释，请放心食用 :point_left:**
## 运行环境
#### Version: Python3
## 安装依赖库
```
暂无
```
## 类目
#### :telephone_receiver:[手机](https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=&pvid=e7b33af1d11d4f70b6d8bdfb8fc7be87)
#### 爬取字段：
- **商品id (id)**
- **商品标题 (title)**
- **商品详情页网址 (url)**
- **商品的网店名称 (shop_name)**
- **商品价格 (price)**
- **商品牌子 (brand)**
- **商品型号 (model)**
- **商品评论数量 (comment_count)**
- **商品好评数 (good_count)**
- **商品中评数 (general_count)**
- **商品差评数 (poor_count)**
- **商品展示数 (show_count)**
- **商品爬取时间 (crawl_date)**
