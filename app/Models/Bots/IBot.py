from abc import abstractmethod
from typing import Dict, Union

import requests

from AWS import SecretsManager, S3
from Models.Instagram.Instagram import InstaGraphAPI
from Models.Picture.Picture import Picture


class IBot:
    __secret: Dict[str, str]
    __s3_bucket: str
    __s3_prefix: str
    __instagraph: InstaGraphAPI

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

        self.__instagraph = InstaGraphAPI(username=username, password=password)

    @property
    def secret(self) -> Dict[str, str]: return self.__secret

    @property
    def s3_bucket(self) -> str: return self.__s3_bucket

    @property
    def s3_prefix(self) -> str: return self.__s3_prefix

    def add_pic_to_s3(self, picture: Picture) -> None:
        with open(picture.local, 'wb') as out_file:
            content = requests.get(picture.source, stream=True).content
            out_file.write(content)

        key = f'{self.s3_prefix}/{picture.title}'
        extra_args = {
            'Metadata': {
                'caption': picture.caption,
                'date': picture.date.strftime("%m-%d-%Y"),
                'source': picture.source
            }
        }
        S3.upload_file(bucket=self.s3_bucket, key=key, location=picture.local, extra_args=extra_args)

    def add_pic_to_instagram(self, photo: Picture) -> None:
        caption = f'{photo.title}\n\nSource: {photo.source}\n\n{photo.caption}'

        self.__instagraph.photo_upload(
            file_path=photo.resize(), caption=caption
        )

    def does_photo_exist(self, picture: Picture) -> bool:
        return S3.does_file_exist(self.s3_bucket, f'{self.s3_prefix}/{picture.title}')

    def run(self) -> None:
        new_pic = self.find_new_pic()
        if new_pic is not None:
            self.add_pic_to_s3(new_pic)
            self.add_pic_to_instagram(new_pic)

    @abstractmethod
    def find_new_pic(self) -> Union[Picture, None]:
        pass
