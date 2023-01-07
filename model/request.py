class Request:
    def __init__(self, probe_request: dict):
        self.id: str = probe_request['context']['id']
        self.name: str = probe_request['context']['name']
        self.target: str = probe_request['context']['target']
        if 'settings' in probe_request:
            self.settings = probe_request['settings']