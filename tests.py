from webtest import TestApp

from emulaterest import EmulateRestMiddleware

def make_app(status, headers, body):
    class ListWithClose(list):
        """Used to test if the close() method of app_iter is called."""
        def __init__(self, app, *args, **kwargs):
            list.__init__(self, *args, **kwargs)
            self.app = app
            self.app.close_called = False

        def close(self):
            self.app.close_called = True

    def app(environ, start_response):
        start_response(status, headers)
        iter_with_close = ListWithClose(app, [body])
        return iter_with_close

    return app

def test_get_form():
    body = '<html><form method="GET">...</form></html>'
    app = make_app('200 OK', [('Content-Type', 'text/html')], body)
    app = TestApp(EmulateRestMiddleware(app))

    resp = app.get('/')

    assert resp.status_int == 200
    assert resp.form.method.upper() == 'GET'
    assert '_method' not in resp

def test_post_form():
    body = '<html><form method="POST">...</form></html>'
    app = make_app('200 OK', [('Content-Type', 'text/html')], body)
    app = TestApp(EmulateRestMiddleware(app))

    resp = app.get('/')

    assert resp.status_int == 200
    assert resp.form.method.upper() == 'POST'
    assert '_method' not in resp

def test_put_form():
    body = """
        <html><form method="PUT" action="/">
            <input type="text" name="inp" value="val">
        </form></html>
        """
    app = make_app('200 OK', [('Content-Type', 'text/html')], body)
    app = TestApp(EmulateRestMiddleware(app))

    resp = app.get('/')

    assert resp.status_int == 200
    assert resp.form.method.upper() == 'POST'
    assert '_method' in resp.form.fields
    assert len(resp.form.fields['_method']) == 1
    assert resp.form.fields['_method'][0].value == 'PUT'

    resp = resp.form.submit()
    req = resp.request

    assert req.method == 'PUT'
    assert not req.GET
    assert 'inp' in req.POST and req.POST['inp'] == 'val'

def test_delete_form():
    body = '<html><form method="DELETE" action="/">...</form></html>'
    app = make_app('200 OK', [('Content-Type', 'text/html')], body)
    app = TestApp(EmulateRestMiddleware(app))

    resp = app.get('/')

    assert resp.status_int == 200
    assert resp.form.method.upper() == 'POST'
    assert '_method' in resp.form.fields
    assert len(resp.form.fields['_method']) == 1
    assert resp.form.fields['_method'][0].value == 'DELETE'

    resp = resp.form.submit()
    req = resp.request

    assert req.method == 'DELETE'
    assert not req.GET
    assert not req.POST

def test_non_200_response():
    body = 'Not Found'
    app = make_app('404 Not Found', [('Content-Type', 'text/html')], body)
    app = TestApp(EmulateRestMiddleware(app))

    resp = app.get('/', status=404)

    assert resp.status_int == 404
    assert resp.content_length == len(body)
    assert resp.body == body

def test_non_html_response():
    body = 'plain text'
    app = make_app('200 OK', [('Content-Type', 'text/plain')], body)
    app = TestApp(EmulateRestMiddleware(app))

    resp = app.get('/')

    assert resp.status_int == 200
    assert resp.content_length == len(body)
    assert resp.body == body

def test_non_empty_content_encoding_response():
    body = '<html>...</html>'
    headers = [('Content-Type', 'text/html'), ('Content-encoding', 'gzip')]
    app = make_app('200 OK', headers, body)
    app = TestApp(EmulateRestMiddleware(app))

    resp = app.get('/')

    assert resp.status_int == 200
    assert resp.content_length == len(body)
    assert resp.body == body

def test_app_iter_close_called():
    body = '<html>...</html>'
    app = make_app('200 OK', [('Content-Type', 'text/html')], body)
    test_app = TestApp(EmulateRestMiddleware(app))

    resp = test_app.get('/')

    assert app.close_called
