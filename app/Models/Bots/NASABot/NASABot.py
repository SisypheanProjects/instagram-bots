from datetime import datetime
from typing import Union

from Models.Bots.IBot import IBot
from Models.Picture.Picture import Picture
from Utilities.Utilities import get


class NASABot(IBot):
    __apod_api_key: str

    def __init__(self, instagram_secret_arn: str, shared_s3_bucket: str):
        # TODO: These strings should be in a config file
        super().__init__(
            instagram_secret_arn,
            "NASA_INSTAGRAM_USERNAME",
            "NASA_INSTAGRAM_PASSWORD",
            shared_s3_bucket,
            "NASA_S3_PREFIX"
        )
        self.__apod_api_key = self.secret["NASA_APOD_API_KEY"]

    def find_new_pic(self) -> Union[Picture, None]:
        # Request latest picture from NASA:
        url = f"https://api.nasa.gov/planetary/apod?api_key={self.__apod_api_key}"
        photo = get(url)

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
