"""
WSGI config for penguins project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguins.settings")

from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

import static

class PartialCling(static.Cling):
    def __call__(self, environ, start_response):
        """
        Hack together something that supports HTTP 206 (Partial Content).
        Yee-haw!
        """
        if environ['REQUEST_METHOD'] not in ('GET', 'HEAD'):
            return self.method_not_allowed(environ, start_response)
        path_info = environ.get('PATH_INFO', '')
        full_path = self._full_path(path_info)
        if not self._is_under_root(full_path):
            return self.not_found(environ, start_response)
        if path.isdir(full_path):
            if full_path[-1] != '/' or full_path == self.root:
                location = util.request_uri(environ, include_query=False) + '/'
                if environ.get('QUERY_STRING'):
                    location += '?' + environ.get('QUERY_STRING')
                headers = [('Location', location)]
                return self.moved_permanently(environ, start_response, headers)
            else:
                full_path = self._full_path(path_info + self.index_file)
        content_type = self._guess_type(full_path)
        try:
            etag, last_modified = self._conditions(full_path, environ)
            headers = [('Date', formatdate(time.time())),
                       ('Last-Modified', last_modified),
                       ('ETag', etag)]
            if_modified = environ.get('HTTP_IF_MODIFIED_SINCE')
            if if_modified and (parsedate(if_modified)
                                >= parsedate(last_modified)):
                return self.not_modified(environ, start_response, headers)
            if_none = environ.get('HTTP_IF_NONE_MATCH')
            if if_none and (if_none == '*' or etag in if_none):
                return self.not_modified(environ, start_response, headers)
            headers.append(('Content-Type', content_type))
            if_range = environ.get('HTTP_RANGE')
            if if_range:
                size = os.path.getsize(full_path)
                byte1, byte2 = 0, None

                m = re.search('(\d+)-(\d*)', range_header)
                g = m.groups()

                if g[0]: byte1 = int(g[0])
                if g[1]: byte2 = int(g[1])

                length = size - byte1
                if byte2 is not None:
                    length = byte2 - byte1

                data = None
                with open(full_path, 'rb') as f:
                    f.seek(byte1)
                    data = f.read(length)

                content_range = "bytes %d-%d/%d" % (byte1,
                    byte1 + length - 1, size)

                headers.append(('Content-Length', size))
                headers.append(('Accept-Ranges', 'bytes'))
                headers.append(('Content-Range', content_range))

                start_response("206 Partial Content", headers)
                return data
            else:
                start_response("200 OK", headers)
                if environ['REQUEST_METHOD'] == 'GET':
                    return self._body(full_path, environ, file_like)
                else:
                    return ['']
        except (IOError, OSError):
            return self.not_found(environ, start_response)


class PartialMediaCling(MediaCling):
    def __init__(self, application, base_dir=None):
        super(PartialMediaCling, self).__init__(application, base_dir)
        self.cling = PartialCling(base_dir)


application = Cling(PartialMediaCling(get_wsgi_application()))
