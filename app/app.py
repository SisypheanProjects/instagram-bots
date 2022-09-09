import os
from typing import List

from Models.Bots.IBot import IBot
from Models.Bots.NASABot.NASABot import NASABot

try:
    INSTAGRAM_SECRET_ARN = os.environ["INSTAGRAM_SECRET_ARN"]
    SHARED_S3_BUCKET = os.environ["SHARED_S3_BUCKET"]
except KeyError:
    INSTAGRAM_SECRET_ARN = "arn:aws:secretsmanager:us-east-2:369635783248:secret:instagram-bots-user-various-secrets-YwDEAO"
    SHARED_S3_BUCKET = "instagram-bots-shared-bucket"

bots: List[IBot] = [
    NASABot(INSTAGRAM_SECRET_ARN, SHARED_S3_BUCKET)
]


def handler(event, context):
    # TODO: Each bot might generate it's own config folder. Look into concurrency issues, and parallelize if safe.
    for bot in bots:
        bot.run()


if __name__ == '__main__':
    handler(None, None)
