# protocol.py

import os
import math
from typing import Tuple, Dict


# Helper function to check if a string represents a number
def is_number(num: str) -> bool:
    try:
        int(num)
        return True
    except ValueError:
        return False


# Create HTTP response headers
def create_header(file_name: str, file_type: str, status_code: str) -> bytes:
    file_size = os.path.getsize(file_name)
    return f"HTTP/1.1 {status_code}\r\nContent-Length: {file_size}\r\nContent-Type: {file_type}\r\n\r\n".encode()


# Fetch data from file (binary or textual)
def get_file_data(file_name: str, file_type: str, msg: str) -> bytes:
    if file_type in ['jpg', 'ico', 'png', 'jpeg', 'gif']:  # binary types
        with open(file_name, 'rb') as file:
            data = file.read()
    else:
        with open(file_name, encoding='UTF-8') as file:
            data = file.readlines()
            if file_name.endswith('empty.html'):
                data[9] = msg  # customize empty page with message
            data = ''.join(data).encode()
    return data


# Handle image file uploads
def handle_upload_image(file_name: str, content_length: int, client_socket) -> str:
    counter = math.ceil(content_length / 10000)
    if file_name.lower().endswith(('.png', '.jpg', 'gif', '.jpeg', '.ico')):
        save_loc = os.getcwd() + '\\webroot\\uploads\\' + file_name
        with open(save_loc, 'wb') as file:
            for _ in range(counter):
                chunk = client_socket.recv(10000)
                file.write(chunk)
        return 'Received successfully'

    for _ in range(counter):
        client_socket.recv(10000)
    return 'Not an image'


# Validate if the HTTP request is properly formed
def validate_http_request(request: str) -> Tuple[bool, str, list]:
    """
    Check if the request is a valid HTTP request. Return True/False, method, and the resource.
    """
    request = request.replace('/', '\\')
    request_lines = request.split('\r\n')
    method, url, version = request_lines[0].split()

    if method in ['GET', 'POST'] and url.startswith('/') and version == 'HTTP/1.1':
        if method == 'POST':
            content_length = int([line.split()[1] for line in request_lines if line.startswith('Content-Length:')][0])
            return True, method, [url, content_length]
        if method == 'GET':
            return True, method, [url]

    return False, '', []
