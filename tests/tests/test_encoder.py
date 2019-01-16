from idempotency_key.encoders import BasicKeyEncoder


def test_basic_encoding():
    class Request:
        path_info = '/myURL/path/'
        method = 'POST'
        POST = {'key': 'value'}

    request = Request()
    obj = BasicKeyEncoder()
    enc_key = obj.encode_key(request, 'MyKey')
    assert enc_key == 'da44e9b4dd5bc8e7853a43c8e8f2d2c2de4394f6614ab37dd5507b6f5988aac4'
