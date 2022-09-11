from datetime import datetime
from typing import Dict, Union

from Utilities.Utilities import get

__url = 'https://api.nasa.gov'
__apod_path = '/planetary/apod'


def apod_get(api_key: str, date: Union[datetime, None] = None) -> Dict:
    query_string = f'api_key={api_key}'
    if date is not None:
        query_string += f'&date={date.strftime("%Y-%m-%d")}'
    return get(__url, __apod_path, query_string)
