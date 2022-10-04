from datetime import date
from typing import Tuple

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
    def title(self) -> str:
        return self.__title

    @property
    def caption(self) -> str:
        return self.__caption

    @property
    def date(self) -> date:
        return self.__date

    @property
    def source(self) -> str:
        return self.__source

    @property
    def local(self) -> str:
        return f'/tmp/{self.__local.replace("/", "")}'

    def resize(self) -> str:
        img = Image.open(self.local)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        new_dimensions = Picture.__new_dimensions(img.height, img.width)
        img_resized = img.resize(new_dimensions)

        resized = f'{self.local}_resized.jpg'
        img_resized.save(resized)

        return resized

    @staticmethod
    def __new_dimensions(original_height: int, original_width: int) -> Tuple[int, int]:     # width, height
        ratio = original_height / original_width

        if ratio == 4 / 5:
            return 1350, 1080
        if ratio == 1:
            return 1080, 1080
        if ratio == 5 / 4:
            return 1080, 1350

        if original_width > original_height:
            # landscape:
            return 1080, 608

        # portrait:
        return 1080, 1350
