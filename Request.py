from typing import Dict, Union


class Request:
    def __init__(self, method: str, url: str, protocol: str, headers: Dict[str, Union[str, int]], data: str = ''):
        self.method = method
        self.url = url
        self.protocol = protocol
        self.headers = headers
        self.data = data
