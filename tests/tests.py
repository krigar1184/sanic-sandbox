async def test_simple_post(test_cli):
    response = await test_cli.get('/')
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {'hello': 'world'}
