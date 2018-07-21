import asyncpg
from sanic.response import json


conn_string = 'postgresql://postgres@localhost:5432/postgres'


async def main(request):
    conn = await asyncpg.connect(conn_string)
    return json({"hello": "world"})
