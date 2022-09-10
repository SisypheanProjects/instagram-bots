from typing import Dict

from Utilities.Utilities import get

__url = 'https://api.nasa.gov'
__apod_path = '/planetary/apod'


def apod_get(api_key: str) -> Dict:
    query_string = f'api_key={api_key}'
    return get(__url, __apod_path, query_string)
