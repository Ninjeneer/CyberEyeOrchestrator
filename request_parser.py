import json
from model.request import Request


def _is_header_valid(request_context: dict) -> bool:
    if request_context is None:
        return False

    if 'id' not in request_context or request_context['id'] == "":
        return False

    if 'name' not in request_context or request_context['name'] == "":
        return False

    if 'target' not in request_context or request_context['target'] == "":
        return False

    return True

def _is_request_valid(request: dict) -> bool:
    if request is None:
        return False

    if not _is_header_valid(request['context']):
        return False

    return True


def parse_request(request: dict) -> Request:
    json_request = json.loads(request)
    if not _is_request_valid(json_request):
        raise Exception("Invalid request")

    return Request(json_request)