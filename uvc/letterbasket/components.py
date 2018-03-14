# -*- coding: utf-8 -*-

import pytz
import grok
import uvcsite

from dolmen.blob import BlobProperty
from zope.interface import implementer
from zope.securitypolicy.interfaces import Allow
from zope.container.interfaces import INameChooser
from zope.dublincore.interfaces import IZopeDublinCore
from zope.securitypolicy.securitymap import SecurityMap
from .interfaces import IMessage, ILetterBasket, IThreadRoot
from dolmen.security.policies.principalrole import ExtraRoleMap


@implementer(IMessage)
class Message(uvcsite.Content, grok.OrderedContainer):
    """ Lastschrift Objekt
    """
    grok.name('Nachricht')
    uvcsite.schema(IMessage)

    attachment = BlobProperty(IMessage['attachment'])

    def __init__(self, *args, **kwargs):
        grok.OrderedContainer.__init__(self, *args, **kwargs)
        uvcsite.Content.__init__(self, *args, **kwargs)
        self.count = 1

    @property
    def meta_type(self):
        return u"Nachricht"

    def getContentType(self):
        return uvcsite.contenttype.bind().get(self)

    def getContentName(self):
        return self.getContentType().__content_type__

    def add(self, content):
        # I think this should be more deterministic
        name = INameChooser(self).chooseName(content.__name__ or '', content)
        self[name] = content

    @property
    def about(self):
        about = {}
        dc = IZopeDublinCore(self)
        about['creator'] = dc.creators and dc.creators[0] or 'Unknown user'
        about['created'] = dc.created
        return about

    @property
    def excludeFromNav(self):
        return True


# Externalized class directive to be able to
# declare Message containing itself.
uvcsite.contenttype.set(Message, Message)


@implementer(ILetterBasket)
class LetterBasket(uvcsite.ProductFolder):
    """ Container fr Lastschrift Objekte
    """
    uvcsite.contenttype(Message)
    title = u"Postfach"


class QuickUserRoleManager(ExtraRoleMap, grok.Adapter):
    grok.context(Message)

    def _compute_extra_data(self):
        extra_map = SecurityMap()
        extra_map.addCell('uvc.Editor', 'servicetelefon-0', Allow)
        return extra_map


class ST(ExtraRoleMap, grok.Adapter):
    grok.context(IThreadRoot)

    def _compute_extra_data(self):
        extra_map = SecurityMap()
        extra_map.addCell('uvc.Editor', 'servicetelefon-0', Allow)
        return extra_map
