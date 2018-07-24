import os
import pytest


def fin():
    for file in os.listdir('./media/storage'):
        os.unlink(os.path.join('./media/storage', file))


@pytest.mark.xfail
async def test_json_success(app, test_cli):
    response = await test_cli.post(
        '/',
        data={'url': 'http://localhost:8003/sample-image.jpeg'},
        headers={'content-type': 'application/json'})

    try:
        assert response.status == 201
    except AssertionError:
        data = await response.json()
        print(data['error'])

    data = await response.json()
    assert data == {'success': True}

    async with app.pool.acquire() as conn:
        count, *_ = await conn.fetchrow('select count(1) from resources')
        assert int(count) == 1

        path, *_ = await conn.fetchrow('select path from resources limit 1')
        assert path == 'json path'

        assert os.path.exists('/storage/media')
        assert len(os.listdir('/storage/media')) == 1


async def test_multipart_success(request, app, test_cli):
    request.addfinalizer(fin)

    response = await test_cli.post('/',
        data={'test_file': open('./tests/media/sample-file', 'rb')},
        headers={'content-type': 'application/octet-stream'},
    )

    data = await response.json()

    try:
        assert response.status == 201
    except AssertionError:
        print(data['error'])

    assert data == {'success': True}

    async with app.pool.acquire() as conn:
        count, *_ = await conn.fetchrow('select count(1) from resources')
        assert int(count) == 1

        path, *_ = await conn.fetchrow('select path from resources limit 1')
        assert path == 'binary path'

        assert len(os.listdir('./media/storage/')) == 1
        
        path = os.listdir('./media/storage')[0]
        assert open(os.path.join('./media/storage', path)).read() == 'This is a sample file.'
