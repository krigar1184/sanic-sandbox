from app.constants import (
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_BINARY,
    ALLOWED_CONTENT_TYPES,
)


def parse_raw_body(body):
    return body.decode('utf8').split('\n\r\n')


def is_content_type_allowed(content_type):
    return content_type in ALLOWED_CONTENT_TYPES


def validate_request(request):
    assert is_content_type_allowed(request.content_type)


def is_binary_request(request):
    return request.content_type == CONTENT_TYPE_BINARY


def is_json_request(request):
    return request.content_type == CONTENT_TYPE_JSON
