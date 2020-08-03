from leetreview import create_app

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_hello(client):
    response = client.get('/hello')
    # b before string represents a "byte string", raw data
    # instead of a specific format
    assert response.data == b'Hello, World!'
