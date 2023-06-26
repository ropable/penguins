from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.encoding import force_str
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView
from urllib import parse


def replace_query_param(url, key, val):
    """Given a URL and a key/val pair, set or replace an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    query_dict[force_str(key)] = [force_str(val)]
    query = parse.urlencode(sorted(query_dict.items()), doseq=True)
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


def remove_query_param(url, key):
    """Given a URL and a key/val pair, remove an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    query_dict.pop(key, None)
    query = parse.urlencode(sorted(query_dict.items()), doseq=True)
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


class ListResourceView(ListView):
    """Generic API list view, having filtering and pagination options as request params.
    Extend with a `model` and `serializer` class.
    """
    http_method_names = ['get', 'options', 'trace']
    model = None
    serializer = None

    def dispatch(self, request, *args, **kwargs):
        # Sanity-check request params.
        if 'offset' in self.request.GET and self.request.GET['offset']:
            try:
                int(self.request.GET['offset'])
            except:
                return HttpResponseBadRequest()
        if 'limit' in self.request.GET and self.request.GET['limit']:
            try:
                int(self.request.GET['limit'])
            except:
                return HttpResponseBadRequest()
        # FIXME: handle user access authorisation in this method.
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Pagination logic.
        count = queryset.count()
        if 'offset' in request.GET and request.GET['offset']:
            offset = int(request.GET['offset'])
        else:
            offset = 0
        if 'limit' in request.GET and request.GET['limit']:
            limit = int(request.GET['limit'])
        else:
            limit = 100  # Default limit

        # Get "next" URL
        if offset + limit > count:
            next_url = None
        else:
            next_url = request.build_absolute_uri()
            next_url = replace_query_param(next_url, 'offset', offset + limit)

        # Get "previous" URL
        if offset <= 0:
            prev_url = None
        else:
            prev_url = request.build_absolute_uri()
            if offset - limit <= 0:
                prev_url = remove_query_param(prev_url, 'offset')
            else:
                prev_url = replace_query_param(prev_url, 'offset', offset - limit)

        queryset = queryset[offset:offset + limit]

        objects = {
            'type': 'FeatureCollection',
            'count': count,
            'next': next_url,
            'previous': prev_url,
            'features': [],
        }

        for obj in queryset:
            objects['features'].append(self.serializer.serialize(obj))

        return JsonResponse(objects)


class DetailResourceView(BaseDetailView):
    """Generic API detail (single object) view.
    Extend with a `model` and `serializer` class.
    """
    http_method_names = ['get', 'options', 'trace']
    model = None
    serializer = None

    def dispatch(self, request, *args, **kwargs):
        # Handle user access authorisation in this method.
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = self.serializer.serialize(obj)
        return JsonResponse(data, safe=False)
