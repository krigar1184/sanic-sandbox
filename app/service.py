import os
import logging
import sys
import aiohttp
from datetime import datetime
from app.constants import CONTENT_TYPE_JSON, CONTENT_TYPE_BINARY


logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stderr,
)
logger = logging.getLogger(__file__)


async def save_resource(app, content_type, data):
    handler = await dispatch(app, content_type)
    resource = Resource(data, handler=handler)

    return await resource.save()


async def dispatch(app, content_type):
    """
    Chooses handler for a specific MIME-type
    """

    async def handle_json(resource):
        data = resource.data
        assert 'url' in data, 'No "url" in data'

        async with aiohttp.ClientSession() as session:
            async with session.get(data['url']) as response:
                content = await response.read()

        path = await resource.save_to_storage(content)
        await resource.save_to_db(app.pool, path)

    async def handle_binary(resource):
        file = resource.data.encode('utf8')
        path = await resource.save_to_storage(file)
        await resource.save_to_db(app.pool, path)

    type_handler_mapping = {
        CONTENT_TYPE_JSON: handle_json,
        CONTENT_TYPE_BINARY: handle_binary,
    }

    try:
        return type_handler_mapping[content_type]
    except KeyError:
        raise Exception  # TODO raise more specific exception


class Resource:
    def __init__(self, data, handler):
        self.data = data
        self.handler = handler

    async def save(self):
        return await self.handler(self)

    async def save_to_storage(self, data):
        filename = 'file-{}'.format(str(datetime.now()))
        storage = './media/storage/'
        os.makedirs(storage, exist_ok=True)

        abspath = os.path.join(storage, filename)

        with open(abspath, 'wb') as f:
            f.write(bytes(data))

        return os.path.relpath(abspath)

    async def save_to_db(self, connection_pool, path):
        async with connection_pool.acquire() as conn:
            await conn.execute('insert into resources(path) values ($1);', path)
