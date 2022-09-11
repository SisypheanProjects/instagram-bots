from datetime import datetime
from typing import Dict, Union

import nasapy as nasapy
from requests import HTTPError

from Utilities.Utilities import get

__url = 'https://api.nasa.gov'
__apod_path = '/planetary/apod'


def apod_get(api_key: str, date: Union[datetime, None] = None) -> Union[Dict, None]:
    # query_string = f'api_key={api_key}'
    # if date is not None:
    #     query_string += f'&date={date.strftime("%Y-%m-%d")}'
    # response = get(__url, __apod_path, query_string)
    #
    # if 'error' in response.keys():
    #     print(f'Request Failed: {response["error"]["code"]}.')
    #     return None
    # return response
    nasa = nasapy.Nasa(api_key)
    if date is not None:
        date = date.strftime("%Y-%m-%d")
    try:
        response = nasa.picture_of_the_day(date=date, hd=True)
        return response
    except HTTPError as e:
        print(f'Could not get a new picture. Error: {e}')
        return None
