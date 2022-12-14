import json
from typing import Dict

import boto3


def get_secret(secret_arn: str) -> Dict:
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(
        SecretId=secret_arn
    )
    return json.loads(response['SecretString'])
