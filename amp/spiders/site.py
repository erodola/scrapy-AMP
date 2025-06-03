import io
from gzip import GzipFile
from urllib.parse import urlsplit, SplitResult
from urllib.parse import parse_qsl as queryparse

import scrapy

from amp.items import Tune
from amp.pipelines import AmpPipeline

import os


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
        
        artist_id = q['view']
        
        all_tunes = response.xpath("//div[@id='result']/table/tr/th[@colspan='6']/../../tr[@class]")
        
        print("")
        print(f"ALL TUNES (artist id {artist_id}):")
        for tune in all_tunes:
            artist = "".join(tune.xpath("./td[2]//text()").getall()).strip()
            title = "".join(tune.xpath("./td[1]//text()").getall()).strip()
            print(f"{artist} - {title}")
        print("")

        for tune in all_tunes:
            artist = "".join(tune.xpath("./td[2]//text()").getall()).strip()
            title = "".join(tune.xpath("./td[1]//text()").getall()).strip()
            
            # Check for missing download link (some artists requested links to be removed)
            
            try:
                link = tune.xpath("./td[1]/a/@href").get().strip()
            except AttributeError:
                print(f"[MISS] Can not retrieve download link for '{artist} - {title}'.")
                continue
                
            fileformat = "".join(tune.xpath("./td[3]//text()").getall()).strip().lower()
            
            # Skip file if it had already been downloaded
            
            filename = AmpPipeline.get_filename(artist=artist, title=title, format=fileformat)
            
            basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'items'))
            basepath = os.path.join(basepath, artist_id)
            
            if os.path.isfile(os.path.join(basepath, filename)):
                print(f"[SKIP] {filename} already exists.")
                continue

            # Download tune
            
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.download_mod,
                meta={
                    "tune": {
                        "id": artist_id,
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
