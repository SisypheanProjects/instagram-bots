import json
import shutil
from abc import abstractmethod
from typing import Dict

import boto3 as boto3
from instabot import Bot


class IBot:
    __bot: Bot
    __secret: Dict[str, str]

    def __init__(self, instagram_secret_arn: str, instagram_user_key: str, instagram_pass_key: str):
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(
            SecretId=instagram_secret_arn
        )
        self.__secret = json.loads(response['SecretString'])
        username = self.__secret[instagram_user_key]
        password = self.__secret[instagram_pass_key]

        # Needed to simplify local work
        try:
            shutil.rmtree('./config')
        except FileNotFoundError:
            pass

        self.__bot = Bot()
        self.__bot.login(username=username, password=password)

    @property
    def bot(self) -> Bot: return self.__bot

    @property
    def secret(self) -> Dict[str, str]: return self.__secret

    @abstractmethod
    def run(self) -> None: pass
