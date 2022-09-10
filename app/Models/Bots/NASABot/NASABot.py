from datetime import datetime
from typing import Union

from APIs import NASA
from Models.Bots.IBot import IBot
from Models.Picture.Picture import Picture


class NASABot(IBot):
    __apod_api_key: str

    def __init__(self, instagram_secret_arn: str, shared_s3_bucket: str, dynamo_db_table: str):
        # TODO: These strings should be in a config file
        super().__init__(
            instagram_secret_arn=instagram_secret_arn,
            instagram_user_secret_key="NASA_INSTAGRAM_USERNAME",
            instagram_pass_secret_key="NASA_INSTAGRAM_PASSWORD",
            dynamo_db_table=dynamo_db_table,
            shared_s3_bucket=shared_s3_bucket,
            s3_prefix="NASA_S3_PREFIX",
            hashtags=["nasa", "space", "explore"]
        )
        self.__apod_api_key = self.secret["NASA_APOD_API_KEY"]

        print('NASABot initialized.')

    def find_new_pic(self) -> Union[Picture, None]:
        photo = NASA.apod_get(self.__apod_api_key)

        url = photo['hdurl']
        if not url:
            url = photo['url']

        file_ext = url.split('.')[-1]
        file = f'/tmp/{photo["title"]}.{file_ext}'
        date = datetime.strptime(photo['date'], '%Y-%m-%d')
        picture = Picture(photo['title'], photo['explanation'], date, url, file)

        if self.does_photo_exist(picture):
            return None
        return picture
