from os import ctermid
from scrapy.spidermiddlewares.httperror import HttpError
from ast import parse
import datetime
import random
import string
import scrapy
from scrapy.http import TextResponse
from twisted.internet.defer import fail
from xgd.items import XgdItem

# 数字 + 英(ASCIIコード表)小文字 + 英(ASCIIコード表)大文字
alphabet = string.digits + string.ascii_lowercase + string.ascii_uppercase

# x.gdのslugは5文字
def gen_slugs(length = 5):
    return ''.join(random.choice(alphabet) for _ in range(length))

class XgdSpiderSpider(scrapy.Spider):
    name = "xgd_spider"
    # すべてのドメインを許可
    allowed_domains = []
    start_urls = ["https://x.gd"]

    custom_settings = {
        # ユーザーエージェント(botじゃない)設定
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja,en;q=0.9",
            "locale": "ja-JP",
        },
        "LOG_FILE": "debug.log",
        "LOG_LEVEL": "DEBUG",
        "LOG_STDOUT": True,
        "STATS_DUMP": True,
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "ROBOTSTXT_OBEY": True,
    }

    # -a nで引数に回数を指定
    def __init__(self, n: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = int(n)
        self.collected = 0
        self.failed = 0

    def start_requests(self):
        init = self.settings.getint("CONCURRENT_REQUESTS_PER_DOMAIN", 4)
        for _ in range(init):
            yield self._next_request()

    def _next_request(self):
        print(f'Total: {self.collected + self.failed} (success: {self.collected}, failed: {self.failed})')
        slug = gen_slugs(5)
        short_url = f'{self.start_urls[0]}/{slug}'
        return scrapy.Request(
            short_url,
            callback=self.parse,
            errback=self.errback,
            meta={"short_url": short_url},
        )

    def parse(self, response):
        create_at = datetime.datetime.now()
        short_url = response.meta.get("short_url")
        # ヘッダはバイト列(b"Hello"は"72 65 6c 6c 6f")で帰ってくるのでutf-8にデコード
        # b'でこれはバイト列と認識させる
        content_type = response.headers.get(b"Content-Type", b"").decode("utf-8", "ignore")
        if "/view/notfound" in response.url.lower():
            yield XgdItem(
                create_at = create_at,
                short_url = short_url,
                url = response.url,
                title = "",
                meta_description = "",
                lang = "",
                content_type = "",
                is_used = False,
            )
            self.failed += 1
            if self.collected < self.n:
                yield self._next_request()
            return
        if not isinstance(response, TextResponse):
            yield XgdItem(
                create_at=create_at,
                short_url=short_url,
                url=response.url,
                title="",
                meta_description="",
                lang="",
                content_type=content_type,
                is_used=False,
                failed=True,
            )
            self.failed += 1
            if self.collected < self.n:
                yield self._next_request()
            return

        title = response.xpath("normalize-space(//title/text())").get()
        # lang=XXXがなければNone
        # strip()で空白消して、lower()で小文字にする
        lang = (response.xpath("//html/@lang").get() or ("")).strip().lower() or None
        # 大文字小文字問わず、<meta NAME="DESCRIOPTION">とかも取れる
        meta_description = response.xpath('//meta[translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="description"]/@content').get()
        if meta_description:
            meta_description = meta_description.strip()

        yield XgdItem(
            create_at = create_at,
            short_url = short_url,
            url = response.url,
            title = title,
            meta_description = meta_description,
            lang = lang,
            content_type = content_type,
            is_used = True,
            failed= False,
        )
        self.collected += 1

        if self.collected < self.n:
            yield self._next_request()

    def errback(self, failure):
        # タイムアウト・DNS失敗・403/5xx等
        # 失敗したリクエストの情報
        request = failure.request
        short_url = request.meta.get("short_url")
        content_type = ""
        if failure.check(HttpError):
            response = failure.value.response
            content_type =response.headers.get(b"Content-Type").decode("utf-8", "ignore")
        # どんなエラーかをprint/log
        self.logger.warning("Request failed: %s (%s)", request.url, failure.value)

        # ScrapyのFailureオブジェクトを使って詳細を取り出せる
        # 例: HTTPエラーかどうか
        if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            print(f"HTTP error {response.status} on {response.url}")
        elif failure.check(scrapy.core.downloader.handlers.http11.TunnelError):
            print(f"Tunnel error on {request.url}")
        else:
            print(f"Other error: {failure.value} on {request.url}")

        yield XgdItem(
            create_at = datetime.datetime.now(),
            short_url= short_url,
            url= request.url,
            title= "",
            meta_description= "",
            lang= "",
            content_type= content_type,
            is_used= True,
            failed= True,
        )

        if self.collected < self.n:
            yield self._next_request()
            self.collected += 1
        return
