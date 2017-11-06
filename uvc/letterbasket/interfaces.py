# -*- coding: utf-8 -*-

from zope import schema
from zope import interface
from zope.location.interfaces import IContained
from zope.container.interfaces import IContainer
from zope.container.constraints import contains
from dolmen.file import FileField


class IThreadRoot(interface.Interface):
    """Marker interface for thread roots
    """


class IMessage(IContained, IContainer):
    contains('.IMessage')

    title = schema.TextLine(
        title=u"Title",
        description=u"Please give a Title",
    )

    subject = schema.TextLine(
        title=u"Subject",
        description=u"Please provide a Subject",
    )

    message = schema.TextLine(
        title=u"Message",
        description=u"Please provide a Message",
    )

    attachment = FileField(
        title=u"Attachment",
        description=u"Please provide a Description",
    )


class ILetterBasket(interface.Interface):
    contains(IMessage)
