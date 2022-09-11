from datetime import datetime
from typing import Dict, Union

import nasapy as nasapy
from requests import HTTPError


def apod_get(api_key: str, date: Union[datetime, None] = None) -> Union[Dict, None]:
    nasa = nasapy.Nasa(api_key)
    if date is not None:
        date = date.strftime("%Y-%m-%d")
    try:
        response = nasa.picture_of_the_day(date=date, hd=True)
        return response
    except HTTPError as e:
        print(f'Could not get a new picture. Error: {e}')
        return None
