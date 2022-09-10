from abc import abstractmethod
from typing import Dict, Union

from instabot import Bot

from AWS import SecretsManager, S3
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

        self.__bot = Bot(
            base_path="/tmp/",
            log_filename="/tmp/log/instabot_{}.log".format(id(self))
        )
        self.__bot.login(username=username, password=password)

    @property
    def secret(self) -> Dict[str, str]: return self.__secret

    @property
    def s3_bucket(self) -> str: return self.__s3_bucket

    @property
    def s3_prefix(self) -> str: return self.__s3_prefix

    def add_pic_to_instagram(self, photo: Picture) -> None:
        caption = f'{photo.title}\n\nSource: {photo.source}'
        self.__bot.upload_photo(
            photo=photo.resize(), caption=caption,
        )

    def does_photo_exist(self, picture: Picture) -> bool:
        return S3.does_file_exist(self.s3_bucket, f'{self.s3_prefix}/{picture.title}')

    def run(self) -> None:
        new_pic = self.add_picture_to_s3()
        if new_pic is not None:
            self.add_pic_to_instagram(new_pic)
        pass

    @abstractmethod
    def add_picture_to_s3(self) -> Union[Picture, None]:
        pass
