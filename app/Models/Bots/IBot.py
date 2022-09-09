import shutil
from abc import abstractmethod
from typing import Dict, Union

from instabot import Bot

from AWS import SecretsManager
from Models.Picture.Picture import Picture


class IBot:
    __bot: Bot
    __secret: Dict[str, str]
    __s3_bucket: str
    __s3_prefix: str

    def __init__(self,
                 instagram_secret_arn: str,
                 instagram_user_key: str,
                 instagram_pass_key: str,
                 s3_bucket: str,
                 s3_prefix: str):

        self.__secret = SecretsManager.get_secret(instagram_secret_arn)
        username = self.__secret[instagram_user_key]
        password = self.__secret[instagram_pass_key]

        self.__s3_bucket = s3_bucket
        self.__s3_prefix = self.__secret[s3_prefix]

        # Needed to simplify local work
        try:
            shutil.rmtree('./config')
        except FileNotFoundError:
            pass

        # self.__bot = Bot()
        # self.__bot.login(username=username, password=password)

    @property
    def bot(self) -> Bot: return self.__bot

    @property
    def secret(self) -> Dict[str, str]: return self.__secret

    @property
    def s3_bucket(self) -> str: return self.__s3_bucket

    @property
    def s3_prefix(self) -> str: return self.__s3_prefix

    def add_pic_to_instagram(self, new_pic: Picture) -> None:
        pass

    def run(self) -> None:
        new_pic = self.add_picture_to_s3()
        if new_pic is not None:
            self.add_pic_to_instagram(new_pic)
        pass

    @abstractmethod
    def add_picture_to_s3(self) -> Union[Picture, None]:
        pass

    @abstractmethod
    def does_photo_exist(self, photo: Picture) -> bool:
        pass
