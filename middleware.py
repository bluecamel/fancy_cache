from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode

from fancy_cache import FancyCache

_HTML_TYPES = ('text/html', 'application/xhtml+xml')

def replace_insensitive(string, target, replacement):
    """
    Borrowed from debug_toolbar: https://github.com/dcramer/django-debug-toolbar

    Original notes:
        Similar to string.replace() but is case insensitive
        Code borrowed from: http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else: # no results so return the original string
        return string

class FancyCacheMiddleware(object):
    """
    Middleware to allow easy management of items cached in
    view or template code.
    """

    def process_request(self, request):
        """
        Add an instance of FancyCache to the request object.
        This happens before views are processed.
        """
        request.fancy_cache = FancyCache()

    def process_response(self, request, response):
        """
        Add the FancyCache panel to the response HTML (just before the close of the body tag).
        Only do this if all of the following are true:
          1) request is not from a crawler, # TODO: see request.is_crawler note below.
          2) the user has permission to view the manager,
          3) the response has a status_code of 200, with HTML content.
        """
        if not settings.FANCY_CACHE_SHOW_PANEL:
            return response

        if not settings.FANCY_CACHE_SHOW_PANEL_IN_ADMIN:
            admin_url = reverse('admin:index')
            if request.path.find(admin_url) == 0:
                return response

        # TODO: Make is_crawler check pluggable (or require detect crawler middleware).
        is_crawler = getattr(request, 'is_crawler', False)
        if is_crawler:
            return response

        if hasattr(request, 'user'):
            if not request.user.has_perm('fancy_cache.view_manager'):
                return response
        else:
            return response

        if response.status_code == 200:
            if response['Content-Type'].split(';')[0] in _HTML_TYPES:
                # Add CSS and javascript.
                head_tag = '</head>'
                response.content = replace_insensitive(
                    smart_unicode(response.content),
                    head_tag,
                    smart_unicode(self.render_head(request) + head_tag)
                )

                # Add panel HTML to body.
                body_tag = '</body>'
                response.content = replace_insensitive(
                    smart_unicode(response.content),
                    body_tag,
                    smart_unicode(self.render_panel(request) + body_tag)
                )
            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)
        return response

    def render_head(self, request):
        """
        Include CSS for the panel.
        """
        return u"""
            <link rel="stylesheet" href="{media_url}css/panel.css" type="text/css" media="screen, projection">
        """.format(media_url=settings.FANCY_CACHE_MEDIA_URL)

    def render_panel(self, request):
        """
        Create the floaty management panel.
        """
        context = {}

        keys = request.fancy_cache.get_keys()

        # Convert vary_on data to HTML.
        for key_type in ('view_keys', 'template_keys'):
            # If there are any keys, show the full panel.
            if len(keys[key_type]) > 0:
                context['show_full_panel'] = True

            context[key_type] = []
            for key, fragment_name, vary_on, expire_time in keys[key_type]:
                context[key_type].append((
                    key,
                    fragment_name,
                    ''.join(['&#%d;' % ord(ch) for ch in str(vary_on)]),
                    expire_time
                ))

    	return render_to_string('fancy_cache/panel.html', context, context_instance=RequestContext(request))
