from pathlib import Path
from typing import Dict, Union

from instagrapi import Client


class InstaGraphAPI:

    __client: Client

    def __init__(self, username: str, password: str):
        self.__client = Client()
        # self.__client.login(username=username, password=password)

    def photo_upload(self, file_path: str, caption: str, extra_data: Union[Dict, None] = None):
        if extra_data is None:
            extra_data = {}
        self.__client.photo_upload(
            path=Path(file_path),
            caption=caption,
            extra_data=extra_data
        )
