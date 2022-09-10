from datetime import date
from typing import Dict, Union

import boto3


class _Column:
    TOPIC = 'topic'
    FILE = 'file'
    DATE_ADDED = 'date-added'
    SOURCE = 'source'


class Record:
    __record: Dict[_Column, str]

    def __init__(self, topic: str, file: str, date_added: date, source: str):
        __record = {
            _Column.TOPIC: {'S': topic},
            _Column.FILE: {'S': file},
            _Column.DATE_ADDED: {'N': date_added.fromtimestamp(0)},
            _Column.SOURCE: {'S': source}
        }


__client = boto3.resource('dynamodb')


def build_record(topic: str, file: str, date_added: date, source: str) -> Record:
    return Record(topic, file, date_added, source)


def add_record(table: str, record: Record) -> None:
    __client.put_item(
        TableName=table,
        Item=record
    )


def record_exists(table: str, record: Record) -> bool:
    pass


def get_record(table: str, record: Record) -> Union[Record, None]:
    pass
