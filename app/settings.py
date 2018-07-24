import os
import asyncpg


DB_PORT = os.environ.get('PGPORT', 5432)
DB_NAME = os.environ.get('POSTGRES_DB', 'postgres')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_HOST = '{}:{}'.format(os.environ.get('POSTGRES_HOST', '127.0.0.1'), DB_PORT)


# database
class db:
    def __init__(self, user, host, db_name):
        self.connection_string = 'postgresql://{}@{}/{}'.format(user, host, db_name)
 
    async def __aenter__(self, **kwargs):
        return await asyncpg.connect(self.connection_string)

    async def __aexit__(self, *args, **kwargs):
        pass
