# imports:
import socket
import os
import math
from Request import Request
from Response import Response

from consts import *
WEB_ROOT_DIR = f'{os.getcwd()}\\webroot'


# Extract parameters from the URL
# Returns a tuple with status, HTTP code, resource, and additional info based on query parameters
def get_params(resource):
    params = resource.split('?')[-1]
    resource = resource.split('?')[0]

    if resource == '/upload' or resource == '/image' or resource == '/calculate-next':
        param = params.split('=')[0]
        value = params.split('=')[-1]

        if (resource == '/upload' and param == 'file-name') or \
                (resource == '/image' and param == 'image-name' and os.path.isfile(UPLOAD_DIR + value)):
            return True, STATUS_OK, resource, value

        if resource == '/calculate-next' and param == 'num' and value.isnumeric():
            return True, STATUS_OK, resource, f'{value} + 1 = {int(value) + 1}'

        return False, '500 Internal Server Error', resource, 'invalid params'

    elif resource == '/calculate-area' or resource == '/check-password':
        first = params.split('&')[0]
        second = params.split('&')[-1]

        first_param, first_value = first.split('=')[0], first.split('=')[-1]
        second_param, second_value = second.split('=')[0], second.split('=')[-1]

        if resource == '/calculate-area' and first_param == 'height' and second_param == 'width' and \
                first_value.isnumeric() and second_value.isnumeric():
            return True, STATUS_OK, resource, str((int(first_value) * int(second_value)) / 2)

        return False, '500 Internal Server Error', resource, 'invalid params'

    return False, '404 Not Found', resource, ' '


# Create HTTP headers for the response
# Returns a dictionary with the 'Content-Length' and 'Content-Type' headers based on the file
def create_header(file_name, file_type):
    return {
        "Content-Length": os.path.getsize(file_name),
        "Content-Type": CONTENT_TYPE_MAP[file_type]
    }


# Read the content of a file (binary or text)
# Returns the file data in bytes, either as raw binary or as encoded text
def get_file_data(file_name, file_type, msg):
    if file_type in FILE_TYPE_CATEGORIES['binary']:
        with open(file_name, 'rb') as f:
            data = f.read()
    else:
        with open(file_name, encoding='UTF-8') as f:
            data = f.readlines()
            if file_name == WEB_ROOT_DIR + '\\empty.html':
                data[9] = msg
            data = ''.join(data).encode()

    return data


# Handle image uploads from the client
# Saves the image to the upload directory if the file is valid
def handle_upload_image(file_name, content_length, client_socket):
    chunk_count = math.ceil(content_length / 10000)
    if file_name.lower().endswith(('.png', '.jpg', 'gif', '.jpeg', '.ico')):
        save_location = UPLOAD_DIR + file_name
        with open(save_location, 'wb') as f:
            for _ in range(chunk_count):
                chunk = client_socket.recv(10000)
                f.write(chunk)
            return 'Received successfully'

    for _ in range(chunk_count):
        client_socket.recv(10000)
    return 'Not an image'


# Handle client requests, determine the appropriate file to serve
# Sends the requested file or error page back to the client
def handle_client_request(request: Request, client_socket):
    resource = request.url
    print("Resource is: " + resource)
    msg = ''

    # Redirect to a different resource if needed
    if resource in REDIRECT_ROUTES:
        status_code = STATUS_REDIRECT
        file_name = WEB_ROOT_DIR + REDIRECT_ROUTES[resource]

    # Serve forbidden pages if the resource is forbidden
    elif resource in FORBIDDEN_PAGES_LIST:
        status_code = STATUS_FORBIDDEN
        file_name = WEB_ROOT_DIR + '\\imgs\\403forbidden.jpg'

    # Serve the default index page if the resource is '/index.html'
    elif resource == '/index.html':
        status_code = STATUS_OK
        file_name = WEB_ROOT_DIR + DEFAULT_URL

    # Serve the requested file if it exists
    elif os.path.isfile(WEB_ROOT_DIR + resource):
        status_code = STATUS_OK
        file_name = WEB_ROOT_DIR + resource

    else:
        valid_params, status_code, url, msg = get_params(resource)
        if valid_params:
            file_name = WEB_ROOT_DIR + '\\empty.html'

            # Handle file upload and save it to the server
            if url == '/upload' and request.method == 'POST':
                msg = handle_upload_image(msg, int(request.headers.get('Content-Length', 0)), client_socket)

            # Serve uploaded image if the request is for '/image'
            elif url == '/image':
                file_name = UPLOAD_DIR + msg

        # Handle 404 Not Found if the resource doesn't exist
        elif status_code == '404 Not Found':
            file_name = WEB_ROOT_DIR + '\\notfound.html'

        else:
            file_name = WEB_ROOT_DIR + '\\empty.html'

    file_type = file_name.split('.')[-1]

    # Check if file type is supported and send the response
    if file_type in CONTENT_TYPE_MAP:
        headers = create_header(file_name, file_type)
        http_data = get_file_data(file_name, file_type, msg)
        response = Response(status_code=status_code, headers=headers, data=http_data)
        client_socket.send(response.to_bytes())


# Validate the incoming HTTP request
# Parses the raw HTTP request string and checks if it follows the correct format
def validate_http_request(request_str: str):
    request_lines = request_str.split('\r\n')
    request_line = request_lines[0].split()

    method = request_line[0]
    url = request_line[1]
    protocol = request_line[2]

    headers = {}
    for line in request_lines[1:]:
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers[key] = value

    if method in ['GET', 'POST'] and protocol == 'HTTP/1.1':
        return True, Request(method, url, protocol, headers)

    return False, None


# Handle the incoming client connection
# Receives the request from the client, validates it, and processes it if valid
def handle_client(client_socket):
    print('Client connected')
    client_request = client_socket.recv(100000).decode()
    print(client_request)
    valid_http, request = validate_http_request(client_request)
    if valid_http:
        print('Got a valid HTTP request')
        handle_client_request(request, client_socket)
    else:
        print('Error: Not a valid HTTP request')
    client_socket.close()


# Main server loop
# Creates a server socket, listens for incoming connections, and handles them
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(10)
    print(f"Listening for connections on port {SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(CONNECTION_TIMEOUT)
        handle_client(client_socket)

if __name__ == '__main__':
    main()
