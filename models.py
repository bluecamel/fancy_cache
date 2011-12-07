from django.db import models

class CacheItem(models.Model):
    """
    Dummy model in order to create permissions.
    I don't love this approach.
    """

    class Meta:
        permissions = (
            ('view_manager', 'Can view the memcached manager.'),
            ('key_delete', 'Can delete memcached keys.'),
        )