import os
import pytest
import json


def fin():
    for file in os.listdir('./media/storage'):
        os.unlink(os.path.join('./media/storage', file))


async def test_wrong_mimetypes(app, test_cli):
    response = await test_cli.post('/',
        data={'test_file': open('./tests/media/sample-file', 'rb')},
        headers={'content-type': 'application/unknown-mimetype'},
    )

    assert response.status == 400
    data = await response.json()
    assert data['success'] == False
    assert data['error'] == 'Wrong content type'


async def test_no_url(app, test_cli):
    response = await test_cli.post('/',
        data=json.dumps({'not_url': 'some_text}'}),
        headers={'content-type': 'application/json'})

    assert response.status == 400
    data = await response.json()
    assert data['success'] == False
    assert data['error'] == 'No "url" in data'


@pytest.mark.xpass("""
TODO this test depends on the internet connection,
better request resource from a local server
""")
async def test_json_success(app, test_cli):
    response = await test_cli.post(
        '/',
        data=json.dumps({'url': 'http://www.cutestpaw.com/wp-content/uploads/2016/02/The-very-dangerous-cat-bear..jpg'}),
        headers={'content-type': 'application/json'})

    assert response.status == 201

    data = await response.json()
    assert data == {'success': True}

    async with app.pool.acquire() as conn:
        path, count = await conn.fetchrow('''
            select path, count(1)
            from resources
            group by path
        ''')

        assert int(count) == 1
        assert os.path.exists(os.path.abspath(path))


async def test_multipart_success(request, app, test_cli):
    request.addfinalizer(fin)

    response = await test_cli.post('/',
        data={'test_file': open('./tests/media/sample-file', 'rb')},
        headers={'content-type': 'application/octet-stream'},
    )

    assert response.status == 201

    data = await response.json()
    assert data == {'success': True}

    async with app.pool.acquire() as conn:
        path, count = await conn.fetchrow('''
            select path, count(1)
            from resources
            group by path
        ''')

    assert int(count) == 1
    assert os.path.exists(os.path.abspath(path))
    assert open(os.path.abspath(path)).read() == 'This is a sample file.'
