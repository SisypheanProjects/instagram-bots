from Bots.IBot import IBot


class NASABot(IBot):

    __apod_api_key: str

    def __init__(self, instagram_secret_arn: str):
        super().__init__(instagram_secret_arn, "NASA_INSTAGRAM_USERNAME", "NASA_INSTAGRAM_PASSWORD")
        self.__apod_api_key = self.secret["NASA_APOD_API_KEY"]

    def run(self):
        pass
