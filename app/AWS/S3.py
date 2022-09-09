from typing import Dict, List, Union

import boto3
from botocore.exceptions import ClientError

__client = boto3.client('s3')


def list_objects(bucket_name: str, prefix: str) -> List[Dict[str, str]]:
    return __client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix,
        StartAfter=f'{prefix}/'
    )['Contents']


def does_file_exist(bucket_name: str, key: str) -> bool:
    try:
        __client.head_object(
            Bucket=bucket_name,
            Key=key
        )
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        # Something went wrong, log it and return False
        # TODO: logs
        return False
    return True


def upload_file(bucket: str, key: str, location: str, extra_args: Union[Dict, None] = None) -> None:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.upload_file(
        Filename=location,
        Key=key,
        ExtraArgs=extra_args
    )
