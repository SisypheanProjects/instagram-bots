from datetime import datetime, timedelta
from typing import Union, Tuple, List

from APIs import NASA
from AWS.DynamoDB import Record
from AWS import S3, DynamoDB
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
                 nasa_apod_secret_key: str,
                 hashtags: List[str]):

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
        self.__apod_api_key = self.secret[nasa_apod_secret_key]

    @staticmethod
    def __get_next_date(dates: List[float], skip_today: bool = False) -> Union[datetime, None]:
        # If we have not seen today's image, return None to pull it.
        # Otherwise, look for the oldest image and pull the previous day's.
        if len(dates) == 0:
            return None

        latest_image = datetime.fromtimestamp(dates[-1]).strftime('%Y-%m-%d')
        today = datetime.today().strftime('%Y-%m-%d')

        if latest_image != today and not skip_today:
            return None

        return datetime.fromtimestamp(dates[0]) - timedelta(days=1)

    def find_new_pic(self) -> Union[Tuple[Record, Picture], None]:
        seen_images = DynamoDB.pull_partition(self.dynamodb_table, self.dynamodb_topic)
        next_date = NASABot.__get_next_date([float(d['date-added']) for d in seen_images])

        found_pic = False
        url = None
        photo = None
        date = None
        record = None
        i = 0
        while not found_pic and i < 10:
            photo = NASA.apod_get(self.__apod_api_key, next_date)

            if photo is None:
                # An API error occurred. Cancel entirely.
                return None

            date = datetime.strptime(photo['date'], '%Y-%m-%d')

            if photo['media_type'] != 'image':
                record = self.build_record(image_id=photo['title'], date_added=date, source='non-image')
                self.update_dynamodb(record)
                if next_date is None:
                    # we tried to pull today's photo, but it is invalid. Pull oldest.
                    next_date = NASABot.__get_next_date([float(d['date-added']) for d in seen_images], skip_today=True)
                    continue
                next_date = next_date - timedelta(days=1)
                continue

            url = photo['hdurl']
            if not url:
                url = photo['url']

            record = self.build_record(image_id=photo['title'], date_added=date, source=url)

            found_pic = True

        if i == 10 or not found_pic:
            # We couldn't find a pic. Stop searching for now.
            return None

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
