from server import WEB_ROOT_DIR

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8000
CONNECTION_TIMEOUT = 30
STATUS_OK = "200 OK"
STATUS_REDIRECT = "302 Found"
STATUS_FORBIDDEN = '403 Forbidden'
DEFAULT_URL = '\\index.html'

FILE_TYPE_CATEGORIES = {'binary': ['jpg', 'ico', 'png', 'jpeg', 'gif'], 'textual': ['js', 'css', 'html']}
CONTENT_TYPE_MAP = {
    "html": "text/html; charset=UTF-8",
    "text": "text/html; charset=UTF-8",
    "jpg": "image/jpg",
    "js": "text/javascript; charset=UTF-8",
    "css": "text/css",
    "ico": "ico",
    "png": "image/png",
    "jpeg": "image/jpeg",
    "gif": "gif"
}

UPLOAD_DIR = WEB_ROOT_DIR + '\\uploads\\'

REDIRECT_ROUTES = {'/': DEFAULT_URL, '//index2.html': DEFAULT_URL}
FORBIDDEN_PAGES_LIST = ['\\empty.html', '\\notfound.html', '\\error500.html']