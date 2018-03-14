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
        title=u"Betreff",
        description=u"Der Betreff Ihrer Nachricht",
    )

    #subject = schema.TextLine(
    #    title=u"Grund",
    #    description=u"Der Grund Ihrer Nachricht",
    #)

    #message = schema.TextLine(
    message = schema.Text(
        title=u"Nachricht",
        description=u"Bitte tragen Sie hier Ihre Nachricht ein",
    )

    attachment = FileField(
        title=u"Anhang",
        required=False,
        description=u"Bitte waehlen Sie die Datei, die Sie uns senden moechten.",
    )

    access_token = schema.TextLine(
        title=u"   ",
        required=False,
    )


class ILetterBasket(interface.Interface):
    contains(IMessage)
