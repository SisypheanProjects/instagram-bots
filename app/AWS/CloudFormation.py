from typing import Union

import boto3

__client = boto3.resource('cloudformation')


def get_stack_output(stack: str, key: str) -> Union[str, None]:
    stack = __client.Stack(stack)
    for output in stack.outputs:
        if output['OutputKey'] == key:
            return output['OutputValue']
    return None
