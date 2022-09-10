from abc import abstractmethod
from typing import Union

from imgurpython import ImgurClient

from Models.Bots.IBot import IBot
from Models.Picture.Picture import Picture


class IImgurBot(IBot):

    __client_id: str
    __client_secret: str
    
    def __init__(self, instagram_secret_arn: str, shared_s3_bucket: str):
        super().__init__(
            instagram_secret_arn,
            "IMGUR_INSTAGRAM_USERNAME",
            "IMGUR_INSTAGRAM_PASSWORD",
            shared_s3_bucket,
            "IMGUR_S3_PREFIX",
            ["imgur", "reddit", "explore"]
        )
        self.__client_id = self.secret["IMGUR_CLIENT_ID"]
        self.__client_secret = self.secret["IMGUR_CLIENT_SECRET"]

        print('IMGURBot initialized.')

    @abstractmethod
    def find_new_pic(self) -> Union[Picture, None]:
        pass





client = ImgurClient(client_id, client_secret)

gallery = client.subreddit_gallery(subreddit='EarthPorn', sort='time', window='week', page=0)
# Example request
items = client.gallery()
for item in items:
    print(item.link)
