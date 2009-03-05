import re
import cgi
import cStringIO

_FORM_RE = re.compile('<form(\s[^>]*\s|\s)method="([a-zA-Z]+)"([^>]*)>',
                      re.IGNORECASE)

class EmulateRestMiddleware(object):
    """WSGI middleware to emulate PUT and DELETE requests.

    The middleware intercepts the wrapped application's response and looks
    for forms with `method="PUT"` or `method="DELETE"`. For each form it
    replaces the method with "POST" and injects a hidden input field
    `_method` that contains the original request method.
    It also intercepts incoming requests and does the inverse transformation.
    """

    def __init__(self, app, force_xhtml=False):
        """The possible options are:

            ``force_xhtml``:
                For documents served as text/html the default behaviour is
                to insert HTML input tags (<input>). If you pass in
                force_xhtml=True, then <input/> tags will be used instead.

                If the document's content type is application/xhtml+xml, then
                XHTML style input elements (<input/>) will be used regardless
                of this parameter.
        """

        self.app = app
        self.force_xhtml = force_xhtml

    def __call__(self, environ, start_response):
        # Do the inverse transformation for the request first
        if environ['REQUEST_METHOD'] == 'POST':
            # We store the original contents of environ['wsgi.input'] in a
            # StringIO instance so that it can be read from later on
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            environ['wsgi.input'] = cStringIO.StringIO(
                environ['wsgi.input'].read(content_length))

            fs = cgi.FieldStorage(fp=environ['wsgi.input'],
                                  environ=environ,
                                  keep_blank_values=True)

            # Reset the stream so that others can read from it later
            environ['wsgi.input'].seek(0)

            if '_method' in fs:
                method = fs['_method'].value
                if method.upper() in ('PUT', 'DELETE'):
                    # TODO: remove '_method' from environ['wsgi.input']
                    environ['REQUEST_METHOD'] = method.upper()

        # Transform the response
        response_args = []
        output = []
        def emulate_start_response(status, response_headers, exc_info=None):
            response_args.extend([status, response_headers, exc_info])
            return output.append

        app_iter = self.app(environ, emulate_start_response)
        status, response_headers, exc_info = response_args

        # Check if we should do the transformation
        transform = True
        if not status.startswith('200'):
            transform = False

        content_type = content_encoding = None
        for h in response_headers:
            if h[0].lower() == 'content-type':
                content_type = h[1]
            elif h[0].lower() == 'content-encoding':
                content_encoding = h[1]

        if (not content_type or
           (not content_type.startswith('text/html') and
            not content_type.startswith('application/xhtml+xml'))):
            transform = False

        if content_encoding:
            transform = False

        # Get the response from the wrapped application
        try:
            output.extend(app_iter)
            response_body = ''.join(output)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

        if transform:
            # Do the transformation
            is_xhtml = (content_type.startswith('application/xhtml+xml') or
                        self.force_xhtml)

            response_body = self.emulate(response_body, is_xhtml)
            response_headers = [h for h in response_headers
                                if h[0].lower() != 'content-length']
            response_headers.append(('Content-Length',
                                     str(len(response_body))))

        start_response(status, response_headers, exc_info)
        return [response_body]

    def emulate(self, body, is_xhtml):
        # TODO: make the name of the hidden input configurable

        close_str = ''
        if is_xhtml:
            close_str = '/'
        repl_pattern = ('<form%(g1)smethod="post"%(g3)s>' +
            '<div style="display:none;"><input type="hidden" ' +
            'name="_method" value="%(g2)s"' + close_str + '></div>')

        def repl(match):
            if match.group(2).upper() in ('PUT', 'DELETE'):
                return repl_pattern % (
                    {'g1': match.group(1),
                     'g2': match.group(2).upper(),
                     'g3': match.group(3)})
            else:
                return match.group(0)

        return _FORM_RE.sub(repl, body)

def emulaterest_filter_factory(global_conf, **kwargs):
    """Can be used as a paste filter factory"""
    def filter(app):
        return EmulateRestMiddleware(app, **kwargs)
    return filter

def emulaterest_filter_app_factory(app, global_conf, **kwargs):
    """Can be used as a paste filter-app factory"""
    return EmulateRestMiddleware(app, **kwargs)
