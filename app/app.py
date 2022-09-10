import multiprocessing
import os
from typing import List

from AWS import CloudFormation
from Models.Bots.IBot import IBot
from Models.Bots.ImgurBots.EarthPicsBot import EarthPicsBot
from Models.Bots.NASABot.NASABot import NASABot

try:
    INSTAGRAM_SECRET_ARN = os.environ["INSTAGRAM_SECRET_ARN"]
    SHARED_S3_BUCKET = os.environ["SHARED_S3_BUCKET"]
    DYNAMO_DB_TABLE = os.environ["DYNAMO_DB_TABLE"]
except KeyError:
    # used for local dev
    INSTAGRAM_SECRET_ARN = CloudFormation.get_stack_output("instagram-bots", "InstagramBotVariousSecrets")
    SHARED_S3_BUCKET = CloudFormation.get_stack_output("instagram-bots", "InstagramBotSharedS3Bucket")
    DYNAMO_DB_TABLE = CloudFormation.get_stack_output("instagram-bots", "InstagramBotDynamoDBTable")

bots: List[IBot] = [
    # NASABot(INSTAGRAM_SECRET_ARN, SHARED_S3_BUCKET, DYNAMO_DB_TABLE),
    EarthPicsBot(INSTAGRAM_SECRET_ARN, SHARED_S3_BUCKET, DYNAMO_DB_TABLE)
]


def handler(event, context):
    if event is not None:
        print(f'event: {event}')
    if context is not None:
        print(f'context: {context}')

    processes = []
    for bot in bots:
        process = multiprocessing.Process(target=bot.run)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


if __name__ == '__main__':
    handler(None, None)
