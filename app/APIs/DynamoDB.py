from datetime import date, datetime
from typing import Dict, Union

import boto3


class _Column:
    TOPIC = 'topic'
    FILE = 'file'
    DATE_ADDED = 'date-added'
    SOURCE = 'source'


class Record:
    __record: Dict[_Column, Dict[str, object]]

    def __init__(self, topic: str, file: str, date_added: datetime, source: str):
        date = datetime(*date_added.timetuple()[:6])
        self.__record = {
            _Column.TOPIC: topic,
            _Column.FILE: file,
            _Column.DATE_ADDED: int((date - datetime(1970, 1, 1)).total_seconds()),
            _Column.SOURCE: source
        }

    def __getitem__(self, item) -> Dict[str, object]:
        return self.__record[item]

    @property
    def record(self) -> Dict: return self.__record


__client = boto3.resource('dynamodb')


def build_record(topic: str, file: str, date_added: date, source: str) -> Record:
    return Record(topic, file, date_added, source)


def add_record(table: str, record: Record) -> None:
    dynamo_table = __client.Table(table)
    dynamo_table.put_item(
        TableName=table,
        Item=record.record
    )


def record_exists(table: str, record: Record) -> bool:
    dynamo_table = __client.Table(table)
    result = dynamo_table.get_item(
        Key={
            _Column.TOPIC: record[_Column.TOPIC],
            _Column.FILE: record[_Column.FILE]
        }
    )
    return 'Item' in result.keys()
