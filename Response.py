from typing import Dict


class Response:
    delimiter = '\r\n'

    def __init__(self, status_code: int, headers: Dict = None, data: bytes = None, protocol: str = 'HTTP/1.1'):
        if headers is None:
            headers = {}
        self.status_code = status_code
        self.protocol = protocol
        self.headers = headers
        self.data = data

    def concat(self) -> str:
        return f"{self.protocol} {self.status_code}{Response.delimiter}{Response.delimiter.join([f'{k}: {v}' for k, v in self.headers.items()])}{Response.delimiter}{Response.delimiter}"

    def to_bytes(self) -> bytes:
        return self.concat().encode('utf-8') + self.data
