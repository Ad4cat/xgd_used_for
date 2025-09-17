from ast import parse
import datetime
from multiprocessing import context
import random
import string
import scrapy
from xgd.items import XgdItem

# 数字 + 英(ASCIIコード表)小文字 + 英(ASCIIコード表)大文字
alphabet = string.digits + string.ascii_lowercase + string.ascii_uppercase

# x.gdのslugは5文字
def gen_slugs(length = 5):
    return ''.join(random.choice(alphabet) for _ in range(length))

class XgdSpiderSpider(scrapy.Spider):
    name = "xgd_spider"
    allowed_domains = ["x.gd"]
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

    def start_requests(self):
        # 重複確認用
        seen = set()
        while len(seen) < self.n:
            slug = gen_slugs(5)
            if slug in seen:
                continue
            seen.add(slug)
            short_url = f'{self.start_urls[0]}/{slug}'
            print(f'now:{len(seen)} / {self.n} -> {short_url}' )
            yield scrapy.Request(
                short_url,
                meta={"short_url": short_url},
                callback=self.parse,
                )

    def parse(self, response):
        create_at = datetime.datetime.now()
        url = response.url
        short_url = response.meta.get("short_url")
        title = response.xpath("normalize-space(//title/text())").get()
        # lang=XXXがなければNone
        # strip()で空白消して、lower()で小文字にする
        lang = (response.xpath("//html/@lang").get() or ("")).strip().lower() or None
        # ヘッダはバイト列(b"Hello"は"72 65 6c 6c 6f")で帰ってくるのでutf-8にデコード
        # b'でこれはバイト列と認識させる
        content_type = response.headers.get(b"Content-Type", b"").decode("utf-8", "ignore")
        # 大文字小文字問わず、<meta NAME="DESCRIOPTION">とかも取れる
        meta_description = response.xpath('//meta[translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="description"]/@content').get()
        if meta_description:
            meta_description = meta_description.strip()

        is_available = True
        if "/view/notfound" in response.url.lower():
            is_available = False

        yield XgdItem(
            create_at = create_at,
            short_url = short_url,
            url = url,
            title = title,
            meta_description = meta_description,
            lang = lang,
            content_type = content_type,
            is_available = is_available,
        )
