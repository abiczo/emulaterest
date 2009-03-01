Emulaterest
===========

WSGI middleware that does Rails style PUT and DELETE request emulation.

The middleware intercepts the wrapped application's response and looks
for forms with `method="PUT"` or `method="DELETE"`. For each form it replaces
the method with "POST" and injects a hidden input field `_method` that contains
the original request method. It also intercepts incoming requests and does
the inverse transformation.

Install
-------

    git clone git://github.com/abiczo/emulaterest.git
    cd emulaterest
    python setup.py install

Notes
-----

* Emulaterest doesn't respect DOCTYPE declarations yet. If you use XHTML,
  incorrect `<input>` tags will be injected.
* If you are using a gzipping middleware or any other middleware that modifies
  the content-encoding, make sure that emulaterest is wrapped in that
  middleware and not the other way round.

Example
-------

Small example using [web.py][web.py]:

    import web

    urls = ('/', 'index')

    class index:
        def GET(self):
            web.ctx['headers'].append(('Content-Type', 'text/html'))
            return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                    "http://www.w3.org/TR/html4/strict.dtd">
                <html><head><title>Emulaterest test</title></head><body><div>
                PUT form:
                <form method="PUT" action="">
                    <div>
                        <input type="text" name="inp" value="value">
                        <input type="submit" value="Submit">
                    </div>
                </form>
                </div></body></html>
                """

        def PUT(self):
            return 'PUT ' + str(web.input())

    app = web.application(urls, globals())
    if __name__ == '__main__':
        import emulaterest
        app.run(emulaterest.EmulateRestMiddleware)

[web.py]: http://webpy.org
