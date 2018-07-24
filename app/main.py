import os

import asyncpg
from sanic import Sanic

from . import settings
from sanic.response import json


app = Sanic()
app.config.from_object(settings)


async def register_db(app):
    port = settings.DB_PORT
    app.pool = await asyncpg.create_pool(dsn='postgresql://postgres@{}:{}/postgres'.format(settings.DB_HOST, port))
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
    from app.service import save_data
    await save_data(app.pool, request.header['Content-Type'])

    return json({"hello": '1'})

app.add_route(main, '/', methods=['GET', 'POST'])

__all__ = ['app']
