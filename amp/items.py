from dataclasses import dataclass


@dataclass
class Item:
    pass


@dataclass
class Tune(Item):
    artist: str
    title: str
    data: bytes
    format: str
    artistId: str
