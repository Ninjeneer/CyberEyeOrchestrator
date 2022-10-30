from model.request import Request


def _is_header_valid(request_header: dict) -> bool:
    if request_header is None:
        return False

    if 'probeName' not in request_header:
        return False

    if 'reportId' not in request_header:
        return False

    if 'probeId' not in request_header:
        return False

    return True

def _is_request_valid(request: dict) -> bool:
    if request is None:
        return False

    if not _is_header_valid(request['header']):
        return False

    return True


def parse_request(request: dict) -> Request:
    if not _is_request_valid(request):
        raise Exception("Invalid request")

    return Request(request)