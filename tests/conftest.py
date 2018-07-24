import os
import asyncpg
import pytest
from sanic import Sanic
from sanic.response import json
from app.service import save_resource
from app.utils import (
    parse_raw_body,
    validate_request,
    is_binary_request,
    is_json_request,
)
from app.constants import (
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_BINARY,
)


TEST_DB_HOST = os.environ.get('TEST_DB_HOST', 'localhost')
TEST_DB_PORT = os.environ.get('TEST_DB_PORT', 8002)
TEST_DB_NAME = os.environ.get('TEST_DB_NAME', 'postgres')
TEST_DB_USER = os.environ.get('TEST_DB_USER', 'postgres')


@pytest.yield_fixture
async def app(request, loop):
    app = Sanic('test_app')
    app.config.from_object({
        'DB_NAME': 'postgres',
        'DB_USER': 'postgres',
        'DB_HOST': 'localhost:8001',
    })

    pool = await asyncpg.create_pool(dsn='postgresql://{}@{}:{}/{}'.format(
        TEST_DB_USER,
        TEST_DB_HOST,
        TEST_DB_PORT,
        TEST_DB_NAME,
    ))

    app.pool = pool

    async def test_main(request):
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

    app.add_route(test_main, '/', methods=['POST'])

    yield app


@pytest.fixture(autouse=True)
def setup(app):
    @app.listener('before_server_start')
    async def create_table(*args):
        async with app.pool.acquire() as conn:
            await conn.execute("""create table if not exists resources (
                id serial primary key,
                path varchar(100),
                created_on timestamp
            );""")

    @app.listener('before_server_start')
    async def create_storage(*args):
        os.makedirs('./media/storage', exist_ok=True)


@pytest.fixture(autouse=True)
def cleanup(app):
    @app.listener('after_server_stop')
    async def _cleanup(*args):
        async with app.pool.acquire() as conn:
            await conn.execute('drop table if exists resources;')


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
