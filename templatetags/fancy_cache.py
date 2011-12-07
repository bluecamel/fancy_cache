from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.template import resolve_variable
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode

register = Library()

class CacheNode(Node):
    def __init__(self, nodelist, expire_time_var, fragment_name, vary_on):
        self.nodelist = nodelist
        self.expire_time_var = Variable(expire_time_var)
        self.fragment_name = fragment_name
        self.vary_on = vary_on

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"fancy_cache" tag got an unknown variable: %r' % self.expire_time_var.var)
        try:
            expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError('"fancy_cache" tag got a non-integer timeout value: %r' % expire_time)

        def render_nodes():
            return self.nodelist.render(context)
        fancy_cache = context['request'].fancy_cache
        value, info = fancy_cache.get_or_set(
            render_nodes,
            self.fragment_name,
            [resolve_variable(var, context) for var in self.vary_on],
            expire_time=expire_time,
            template=True,
            verbose=True
        )

        user = context.get('user', None)
        if user.has_perm('fancy_cache.view_manager'):
            return u"""
                <!-- fancy_cache ..::.. {key} ..::.. {vary_args} -->
                <div id="fancy_cache_item_{key}" class="fancy_cache_wrapper">
                {value}
                </div>
                <!-- end_fancy_cache ..::.. {key} ..::.. {vary_args} -->
            """.format(
                key=info['key'],
                value=value,
                vary_args=info['vary_args']
            )
        else:
            return value

def do_cache(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time.

    Usage::

        {% load fancy_cache %}
        {% fancy_cache [expire_time] [fragment_name] %}
            .. some expensive processing ..
        {% end_fancy_cache %}

    This tag also supports varying by a list of arguments::

        {% load fancy_cache %}
        {% fancy_cache [expire_time] [fragment_name] [var1] [var2] .. %}
            .. some expensive processing ..
        {% end_fancy_cache %}

    Each unique set of arguments will result in a unique cache entry.
    """
    nodelist = parser.parse(('end_fancy_cache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    return CacheNode(nodelist, tokens[1], tokens[2], tokens[3:])

register.tag('fancy_cache', do_cache)