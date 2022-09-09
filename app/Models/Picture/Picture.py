from datetime import date


class Picture:
    __title: str
    __caption: str
    __date: date
    __source: str

    def __init__(self, title: str, caption: str, date: date, source: str):
        self.__title = title
        self.__caption = caption
        self.__date = date
        self.__source = source

    @property
    def title(self) -> str: return self.__title

    @property
    def caption(self) -> str: return self.__caption

    @property
    def date(self) -> date: return self.__date

    @property
    def source(self) -> str: return self.__source
