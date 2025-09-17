from tqdm import tqdm
from scrapy import signals

class TqdmExtension:
    def __init__(self, stats):
        self.stats = stats
        self.pbar = None

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.stats)
        # spiderがopenしたときにext.spider_openedを呼ぶ
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        # itemがscrapeされたらext.item_scrapedを呼ぶ
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        # spiderがcloseしたらext.item_closedを呼ぶ
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        # -a n=Xからtotalをもらう
        self.pbar = tqdm(total=spider.n, desc="Scraped items")

    def item_scraped(self, item, response, spider):
        # ext.item_scrapedが呼ばれるたびにprogbarを1進める
        self.pbar.update(1)

    def spider_closed(self, spider):
        self.pbar.close()
