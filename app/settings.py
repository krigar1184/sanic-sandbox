import os
import asyncpg


DB_PORT = os.environ.get('PGPORT', 5432)
DB_NAME = os.environ.get('POSTGRES_DB', 'postgres')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_HOST = '{}:{}'.format(os.environ.get('POSTGRES_HOST', '127.0.0.1'), DB_PORT)


TEST_DB_HOST = os.environ.get('TEST_DB_HOST', 'localhost')
TEST_DB_PORT = os.environ.get('TEST_DB_PORT', 8002)
TEST_DB_NAME = os.environ.get('TEST_DB_NAME', 'postgres')
TEST_DB_USER = os.environ.get('TEST_DB_USER', 'postgres')
