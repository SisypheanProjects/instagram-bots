import os
from typing import List

from AWS import CloudFormation
from Models.Bots.IBot import IBot
from Models.Bots.NASABot.NASABot import NASABot

try:
    INSTAGRAM_SECRET_ARN = os.environ["INSTAGRAM_SECRET_ARN"]
    SHARED_S3_BUCKET = os.environ["SHARED_S3_BUCKET"]
except KeyError:
    INSTAGRAM_SECRET_ARN = CloudFormation.get_stack_output("instagram-bots", "InstagramBotVariousSecrets")
    SHARED_S3_BUCKET = CloudFormation.get_stack_output("instagram-bots", "InstagramSharedS3Bucket")

bots: List[IBot] = [
    NASABot(INSTAGRAM_SECRET_ARN, SHARED_S3_BUCKET)
]


def handler(event, context):
    print(event)
    print(context)
    # TODO: Each bot might generate it's own config folder. Look into concurrency issues, and parallelize if safe.
    for bot in bots:
        bot.run()


if __name__ == '__main__':
    handler(None, None)
