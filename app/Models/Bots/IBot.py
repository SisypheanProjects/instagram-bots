from abc import abstractmethod
from datetime import date, datetime
from typing import Dict, Union, List, Tuple

import requests

from APIs import DynamoDB
from APIs.DynamoDB import Record
from AWS import SecretsManager, S3
from Models.Instagram.Instagram import InstaGraphAPI
from Models.Picture.Picture import Picture


class IBot:
    __secret: Dict[str, str]
    __s3_bucket: str
    __s3_prefix: str
    __dynamo_db_table: str
    __dynamo_db_topic: str
    __insta_graph_api: InstaGraphAPI
    __hashtags: List[str]

    def __init__(self,
                 instagram_secret_arn: str,
                 instagram_user_secret_key: str,
                 instagram_pass_secret_key: str,
                 dynamo_db_table: str,
                 dynamo_db_topic: str,
                 shared_s3_bucket: str,
                 s3_prefix: str,
                 hashtags: List[str]):

        self.__secret = SecretsManager.get_secret(instagram_secret_arn)
        username = self.__secret[instagram_user_secret_key]
        password = self.__secret[instagram_pass_secret_key]

        self.__s3_bucket = shared_s3_bucket
        self.__s3_prefix = self.__secret[s3_prefix]

        self.__dynamo_db_table = dynamo_db_table
        self.__dynamo_db_topic = dynamo_db_topic

        self.__hashtags = hashtags

        self.__insta_graph_api = InstaGraphAPI(username=username, password=password)

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

        key = f'{self.s3_prefix}/{IBot.__date_string(picture.date)}-{picture.title}'
        extra_args = {
            'Metadata': {
                'caption': picture.caption,
                'source': picture.source,
                'date': IBot.__date_string(picture.date)
            }
        }
        S3.upload_file(bucket=self.s3_bucket, key=key, location=picture.local, extra_args=extra_args)

    def __caption_string(self, picture: Picture) -> str:
        caption = f'{picture.title}\n\n'
        caption += f'Source: {picture.source}\n\n'
        caption += f'{picture.caption}\n\n'
        for tag in self.__hashtags:
            caption += f'#{tag} '

        return caption

    @staticmethod
    def __date_string(date_: date) -> str:
        return date_.strftime("%m-%d-%Y")

    def build_record(self, image_id: str, date_added: datetime, source: str) -> Record:
        return DynamoDB.build_record(
            topic=self.__dynamo_db_topic,
            file=image_id,
            date_added=date_added,
            source=source
        )

    def add_pic_to_instagram(self, picture: Picture) -> None:
        caption = self.__caption_string(picture)

        self.__insta_graph_api.photo_upload(
            file_path=picture.resize(), caption=caption
        )

    def does_photo_exist(self, record: Record) -> bool:
        return DynamoDB.record_exists(self.__dynamo_db_table, record)

    def update_dynamodb(self, record: Record) -> None:
        DynamoDB.add_record(self.__dynamo_db_table, record)

    def run(self) -> None:
        record, new_pic = self.find_new_pic()
        if new_pic is not None:
            self.update_dynamodb(record)
            self.add_pic_to_s3(new_pic)
            self.add_pic_to_instagram(new_pic)

    @abstractmethod
    def find_new_pic(self) -> Union[Tuple[Record, Picture], None]:
        pass
