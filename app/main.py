import asyncpg
from sanic import Sanic

from . import settings
from sanic.response import json
from app.service import save_resource
from app.utils import (
    parse_raw_body,
    validate_request,
    is_binary_request,
    is_json_request,
)


app = Sanic()
app.config.from_object(settings)


async def register_db(app):
    conn_string = 'postgresql://{}@{}/{}'.format(
        settings.DB_USER,
        settings.DB_HOST,
        settings.DB_USER,
    )
    app.pool = await asyncpg.create_pool(conn_string)
    async with app.pool.acquire() as conn:
        await conn.execute("""create table if not exists resources (
            id serial primary key,
            path varchar(100),
            created_on timestamp
        );""")


@app.listener('before_server_start')
async def before_server_start(app, loop):
    await register_db(app)


async def main(request):
    """
    The main route. Accepts POST requests with the following "Content-Type" headers:
    - application/json
    - octet-stream

    If the request has a json content type, then the request body should contain a "url" key
    with the location from where the resource should be downloaded. In case of the octet-stream,
    the binary data is considered a resource.
    """
    try:
        validate_request(request)  # TODO move to middleware
    except AssertionError:
        return json({'success': False, 'error': 'Wrong content type'}, 400)

    if is_binary_request(request):
        try:
            header, data, encoded_data = parse_raw_body(request.body)
        except Exception:
            return json({'success': False, 'error': 'Failed to parse request body'}, 400)
    elif is_json_request(request):
        data = request.load_json()
    else:
        return json({'success': False, 'error': 'Wrong content type'}, 400)

    try:
        await save_resource(app, request.content_type, data)
    except Exception as e:
        return json({'success': False, 'error': str(e)}, 400)

    return json({'success': True}, 201)


app.add_route(main, '/', methods=['GET', 'POST'])

__all__ = ['app']
