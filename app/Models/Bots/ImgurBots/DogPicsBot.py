from Models.Bots.ImgurBots.IImgurBot import IImgurBot


class DogPicsBot(IImgurBot):

    def __init__(self, instagram_secret_arn: str, shared_s3_bucket: str, dynamo_db_table: str):
        super().__init__(
            instagram_secret_arn=instagram_secret_arn,
            shared_s3_bucket=shared_s3_bucket,
            subreddit='rarepuppers',
            dynamo_db_topic='dog-pics',
            dynamo_db_table=dynamo_db_table,
            instagram_user_secret_key='DOGPICS_INSTAGRAM_USERNAME',
            instagram_pass_secret_key='DOGPICS_INSTAGRAM_PASSWORD',
            imgur_s3_prefix_secret_key='DOGPICS_S3_PREFIX',
            hashtags=['dog', 'pet', 'reddit', 'imgur']
        )

        print('DogPicsBot initialized.')