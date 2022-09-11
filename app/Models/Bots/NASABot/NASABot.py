from datetime import datetime, timedelta
from typing import Union, Tuple, List

from APIs import NASA, DynamoDB
from APIs.DynamoDB import Record
from Models.Bots.IBot import IBot
from Models.Picture.Picture import Picture


class NASABot(IBot):
    __apod_api_key: str

    def __init__(self,
                 bot_name: str,
                 disable_instagram: bool,
                 instagram_secret_arn: str,
                 dynamo_db_table: str,
                 shared_s3_bucket: str,
                 dynamo_db_topic: str,
                 instagram_user_secret_key: str,
                 instagram_pass_secret_key: str,
                 imgur_s3_prefix_secret_key: str,
                 hashtags: List[str]):

        # TODO: These strings should be in a config file
        super().__init__(
            bot_name=bot_name,
            disable_instagram=disable_instagram,
            instagram_secret_arn=instagram_secret_arn,
            instagram_user_secret_key=instagram_user_secret_key,
            instagram_pass_secret_key=instagram_pass_secret_key,
            dynamo_db_table=dynamo_db_table,
            dynamo_db_topic=dynamo_db_topic,
            shared_s3_bucket=shared_s3_bucket,
            s3_prefix=imgur_s3_prefix_secret_key,
            hashtags=hashtags
        )
        self.__apod_api_key = self.secret["NASA_APOD_API_KEY"]

    def find_new_pic(self) -> Union[Tuple[Record, Picture], None]:
        photo = NASA.apod_get(self.__apod_api_key)

        url = photo['hdurl']
        if not url:
            url = photo['url']

        date = datetime.strptime(photo['date'], '%Y-%m-%d')

        record = self.build_record(image_id=photo['title'], date_added=date, source=url)
        while not self.does_photo_exist(record):
            date = date - timedelta(days=1)
            photo = NASA.apod_get(self.__apod_api_key, date)
            record = self.build_record(image_id=photo['title'], date_added=date, source=url)

        file_ext = url.split('.')[-1]
        file = f'/tmp/{photo["title"]}.{file_ext}'
        picture = Picture(
            title=photo['title'],
            caption=photo['explanation'],
            date=date,
            source=url,
            local=file
        )

        return record, picture
