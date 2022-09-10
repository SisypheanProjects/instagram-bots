import ast
from typing import Union, Dict

import requests


def get(url: str, path: str, query_string: Union[str, None] = None) -> Dict:
    address = f'{url}{path}'
    if query_string is not None:
        address += f'?{query_string}'
    response = requests.get(address)
    return ast.literal_eval(response.content.decode('utf-8'))
