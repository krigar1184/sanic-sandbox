import asyncpg
from sanic.response import json


conn_string = f'postgresql://postgres@localhost:8001/postgres'


async def main(request):
    conn = await asyncpg.connect(conn_string)
    return json({"hello": "world"})