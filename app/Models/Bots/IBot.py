from abc import abstractmethod
from datetime import date, datetime
from typing import Dict, Union, List, Tuple

import requests
from instagrapi.exceptions import RateLimitError

from APIs import DynamoDB
from APIs.DynamoDB import Record
from AWS import SecretsManager, S3
from Models.Instagram.Instagram import InstaGraphAPI
from Models.Picture.Picture import Picture


class IBot:
    __bot_name: str
    __username: str
    __secret: Dict[str, str]
    __s3_bucket: str
    __s3_prefix: str
    __dynamo_db_table: str
    __dynamo_db_topic: str
    __disable_instagram: bool
    __insta_graph_api: Union[InstaGraphAPI, None]
    __hashtags: List[str]

    def __init__(self,
                 bot_name: str,
                 disable_instagram: bool,
                 instagram_secret_arn: str,
                 instagram_user_secret_key: str,
                 instagram_pass_secret_key: str,
                 dynamo_db_table: str,
                 dynamo_db_topic: str,
                 shared_s3_bucket: str,
                 s3_prefix: str,
                 hashtags: List[str]):

        self.__bot_name = bot_name
        self.__disable_instagram = disable_instagram
        self.__secret = SecretsManager.get_secret(instagram_secret_arn)
        self.__username = self.__secret[instagram_user_secret_key]
        password = self.__secret[instagram_pass_secret_key]

        self.__s3_bucket = shared_s3_bucket
        self.__s3_prefix = self.__secret[s3_prefix]

        self.__dynamo_db_table = dynamo_db_table
        self.__dynamo_db_topic = dynamo_db_topic

        self.__hashtags = hashtags

        if not disable_instagram:
            try:
                self.__insta_graph_api = InstaGraphAPI(username=self.__username, password=password)
            except RateLimitError:
                print(f'{bot_name} -- Cannot instantiate InstaGraphiAPI for {self.__username} due to RateLimitError.')
                self.__insta_graph_api = None
            except Exception as e:
                print(f'{bot_name} -- Cannot instantiate InstaGraphAPI. Error: {e}')
                self.__insta_graph_api = None

            if self.__insta_graph_api is not None:
                print(f'{bot_name} -- Successfully initialized.')
        else:
            self.__insta_graph_api = None
            print(f'{bot_name} -- Disable Instagram flag is present in config. Not initializing InstaGraphAPI.')

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
        if not self.__disable_instagram:
            if self.__insta_graph_api is None:
                print(f'{self.__bot_name} -- Was not able to start Instagram Service. Exiting.')
                return

        print(f'{self.__bot_name} -- searching for a new picture.')
        picture = self.find_new_pic()
        if picture is not None:
            # Unpack the tuple returned from find_new_pic:
            (record, new_pic) = picture

            print(f'{self.__bot_name} -- uploading new picture to S3.')
            self.add_pic_to_s3(new_pic)
            if not self.__disable_instagram:
                print(f'{self.__bot_name} -- adding new picture to Instagram.')
                self.add_pic_to_instagram(new_pic)
            else:
                print(f'{self.__bot_name} -- Disable Instagram flag is present in config. Will not attempt to update Instagram.')
            print(f'{self.__bot_name} -- updating DynamoDB.')
            self.update_dynamodb(record)
            print(f'{self.__bot_name} -- complete.')
        else:
            print(f'{self.__bot_name} -- Could not find a new picture.')

    @abstractmethod
    def find_new_pic(self) -> Union[Tuple[Record, Picture], None]:
        pass
