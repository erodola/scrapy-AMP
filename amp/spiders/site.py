import io
from gzip import GzipFile
from urllib.parse import urlsplit, SplitResult
from urllib.parse import parse_qsl as queryparse

import scrapy

from amp.items import Tune


class SiteSpider(scrapy.Spider):
    allowed_domains = [
        'amp.dascene.net',
    ]

    start_urls = [
        'http://amp.dascene.net/',
    ]

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError()


class ArtistSpider(SiteSpider):
    """
    Download all artist mods
    """
    name = 'artist'

    def __init__(self, id: str = ""):
        """
        :param id: Artist ID
        """

        if id == "":
            id = None

        if id is None:
            raise ValueError("empty ID")

        self.start_urls = [
            f"https://amp.dascene.net/detail.php?detail=modules&view={id}"
        ]

    def parse(self, response: scrapy.http.Response):
        """
        Get list of tunes
        """

        u: SplitResult = urlsplit(response.url)
        q: dict = dict(queryparse(u.query))

        for tune in response.xpath("//div[@id='result']/table/tr/th[@colspan='6']/../../tr[@class]"):
            artist = "".join(tune.xpath("./td[2]//text()").getall()).strip()
            title = "".join(tune.xpath("./td[1]//text()").getall()).strip()
            link = tune.xpath("./td[1]/a/@href").get().strip()
            fileformat = "".join(tune.xpath("./td[3]//text()").getall()).strip().lower()

            # Download tune
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.download_mod,
                meta={
                    "tune": {
                        "id": q['view'],
                        "artist": artist,
                        "title": title,
                        "format": fileformat,
                    }
                },
            )

    def download_mod(self, response: scrapy.http.Response):
        """
        Download compressed tracker music
        :param response:
        :return:
        """

        ctype = response.headers.get('Content-Type').decode('utf-8')
        if ctype != 'application/x-gzip':
            raise ValueError(f"Invalid content-type '{ctype}'")

        with GzipFile(fileobj=io.BytesIO(response.body), mode='rb') as f:
            uncompressed = f.read()
            yield Tune(
                format=response.meta["tune"]["format"],
                artist=response.meta["tune"]["artist"],
                title=response.meta["tune"]["title"],
                data=uncompressed,
                artistId=response.meta["tune"]["id"],
            )
