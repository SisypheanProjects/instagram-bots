import multiprocessing
import os
from typing import List

import yaml
from yaml import Loader

from AWS import CloudFormation
from Models.Bots.IBot import IBot
from Models.Bots.ImgurBots.ImgurBot import ImgurBot
from Models.Bots.NASABot.NASABot import NASABot

stream = open("config.yaml", 'r')
config = yaml.load(stream, Loader=Loader)
stack_name = config['StackName']
stack_output_keys = config['StackOutputKeys']
disable_instagram = config['DisableInstagram']

try:
    INSTAGRAM_SECRET_ARN = os.environ["INSTAGRAM_SECRET_ARN"]
    SHARED_S3_BUCKET = os.environ["SHARED_S3_BUCKET"]
    DYNAMO_DB_TABLE = os.environ["DYNAMO_DB_TABLE"]
except KeyError:
    # used for local dev
    INSTAGRAM_SECRET_ARN = CloudFormation.get_stack_output(stack_name, stack_output_keys['SecretARN'])
    SHARED_S3_BUCKET = CloudFormation.get_stack_output(stack_name, stack_output_keys['SharedS3Bucket'])
    DYNAMO_DB_TABLE = CloudFormation.get_stack_output(stack_name, stack_output_keys['DynamoDBTable'])

bots: List[IBot] = []

for bot in config['Bots']['ImgurBots']:
    name = bot['Name']
    dynamo_topic = bot['DynamoDBTopic']
    instagram_secret_keys = bot['InstagramAccountSecretKeys']
    hashtags = bot['HashTags']
    subreddit = bot['Subreddit']

    bots.append(ImgurBot(
        bot_name=name,
        disable_instagram=disable_instagram,
        instagram_secret_arn=INSTAGRAM_SECRET_ARN,
        shared_s3_bucket=SHARED_S3_BUCKET,
        dynamo_db_table=DYNAMO_DB_TABLE,
        dynamo_db_topic=dynamo_topic,
        subreddit=subreddit,
        instagram_user_secret_key=instagram_secret_keys['UserName'],
        instagram_pass_secret_key=instagram_secret_keys['Password'],
        imgur_s3_prefix_secret_key=instagram_secret_keys['S3Prefix'],
        hashtags=hashtags
    ))

nasa_bot_config = config['Bots']['NASABot']
bots.append(NASABot(
    bot_name=nasa_bot_config['Name'],
    disable_instagram=disable_instagram,
    instagram_secret_arn=INSTAGRAM_SECRET_ARN,
    dynamo_db_table=DYNAMO_DB_TABLE,
    shared_s3_bucket=SHARED_S3_BUCKET,
    dynamo_db_topic=nasa_bot_config['DynamoDBTopic'],
    instagram_user_secret_key=nasa_bot_config['InstagramAccountSecretKeys']['UserName'],
    instagram_pass_secret_key=nasa_bot_config['InstagramAccountSecretKeys']['Password'],
    imgur_s3_prefix_secret_key=nasa_bot_config['InstagramAccountSecretKeys']['S3Prefix'],
    nasa_apod_secret_key=nasa_bot_config['InstagramAccountSecretKeys']['APODKey'],
    hashtags=nasa_bot_config['HashTags']
))


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
