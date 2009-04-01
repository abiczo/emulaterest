===========
EmulateRest
===========

WSGI middleware that does Rails style PUT and DELETE request emulation.

The middleware intercepts the wrapped application's response and looks
for forms with ``method="PUT"`` or ``method="DELETE"``. For each such form
it replaces the value of ``method`` with "POST" and adds a hidden input
field ``_method`` that contains the original request method.
It also intercepts incoming requests and does the inverse transformation.

What this all means is that you can use PUT and DELETE forms in your
HTML code, without having to worry about browser support for these
request methods.

Install
=======
::

    git clone git://github.com/abiczo/emulaterest.git
    cd emulaterest
    python setup.py install

Notes
=====

* For ``text/html`` documents the default behavior is to inject HTML style
  ``<input>`` elements. You can tell EmulateRest to inject XHTML style
  ``<input/>`` elements either by using the ``force_xhtml`` option or by
  serving your documents as ``application/xhtml+xml``.

* If you are using a gzipping middleware or any other middleware that modifies
  the content-encoding, make sure that EmulateRest is wrapped in that
  middleware and not the other way round.

Example
=======

A complete working example using `web.py <http://webpy.org>`_::

    import web

    urls = ('/', 'index')

    class index:
        def GET(self):
            web.ctx['headers'].append(('Content-Type', 'text/html'))
            return """<html><head><title>PUT test</title></head><body><div>
                <form method="PUT" action="/">
                    <div>
                        <input type="text" name="inp" value="value">
                        <input type="submit" value="Submit">
                    </div>
                </form>
                </div></body></html>
                """

        def PUT(self):
            return 'PUT ' + str(web.input())

    if __name__ == '__main__':
        import emulaterest
        app = web.application(urls, globals())
        app.run(emulaterest.EmulateRestMiddleware)
