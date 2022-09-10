from datetime import date

from PIL import Image


class Picture:
    __title: str
    __caption: str
    __date: date
    __source: str
    __local: str

    def __init__(self, title: str, caption: str, date: date, source: str, local: str):
        self.__title = title
        self.__caption = caption
        self.__date = date
        self.__source = source
        self.__local = local

    @property
    def title(self) -> str: return self.__title

    @property
    def caption(self) -> str: return self.__caption

    @property
    def date(self) -> date: return self.__date

    @property
    def source(self) -> str: return self.__source

    @property
    def local(self) -> str: return self.__local

    def resize(self) -> str:
        resized = f'{self.title}_resized.jpg'
        im = Image.open(self.local)
        new_size = (1080, 1350)
        im1 = im.resize(new_size)
        im1.save(resized)
        return resized
