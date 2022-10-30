class Request:
    def __init__(self, queue_request: dict):
        self.probe_id: str = queue_request['header']['probeId']
        self.report_id: str = queue_request['header']['reportId']
        self.probe_name: str = queue_request['header']['probeName']

        self.env: dict = queue_request['body']['env']