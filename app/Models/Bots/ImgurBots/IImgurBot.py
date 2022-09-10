from datetime import datetime
from typing import Union, List

from imgurpython import ImgurClient
from pydantic.class_validators import Tuple

from APIs import DynamoDB
from APIs.DynamoDB import Record
from Models.Bots.IBot import IBot
from Models.Picture.Picture import Picture


class IImgurBot(IBot):

    __client: ImgurClient
    __subreddit: str

    def __init__(self,
                 instagram_secret_arn: str,
                 shared_s3_bucket: str,
                 dynamo_db_table: str,
                 subreddit: str,
                 topic: str,
                 instagram_user_secret_key: str,
                 instagram_pass_secret_key: str,
                 imgur_s3_prefix_secret_key: str,
                 hashtags: List[str]):

        super().__init__(
            instagram_secret_arn=instagram_secret_arn,
            instagram_user_secret_key=instagram_user_secret_key,
            instagram_pass_secret_key=instagram_pass_secret_key,
            dynamo_db_table=dynamo_db_table,
            dynamo_db_topic=topic,
            shared_s3_bucket=shared_s3_bucket,
            s3_prefix=imgur_s3_prefix_secret_key,
            hashtags=hashtags
        )

        self.__subreddit = subreddit
        self.__client = ImgurClient(self.secret["IMGUR_CLIENT_ID"], self.secret["IMGUR_CLIENT_SECRET"])

    def find_new_pic(self, page: int = 0) -> Union[Tuple[Record, Picture], None]:
        if page == 5:
            return None

        gallery = self.__client.subreddit_gallery(
            subreddit=self.__subreddit,
            sort='time',
            window='week',
            page=page
        )

        for image in gallery:
            record = self.build_record(image.id, datetime.fromtimestamp(image.datetime), image.link)

            if self.does_photo_exist(record):
                continue

            return record, IImgurBot.__build_picture(image)
        return self.find_new_pic(page + 1)

    @staticmethod
    def __build_picture(image) -> Picture:
        local = f'/tmp/{image.title}'
        return Picture(
            title=image.title,
            caption='',
            date=datetime.fromtimestamp(image.datetime),
            source=image.link,
            local=local)
