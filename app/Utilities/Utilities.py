import ast

import requests


def get(url: str):
    response = requests.get(url)
    return ast.literal_eval(response.content.decode('utf-8'))
