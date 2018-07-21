import pytest
from sanic import Sanic

from app.routes import main


@pytest.yield_fixture
def app():
    app = Sanic('test_app')
    app.config.from_object({
        'DB_NAME': 'test',
        'DB_USER': 'postgres',
        'DB_HOST': 'localhost:5432'
    })

    app.add_route(main, '/')

    yield app


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
