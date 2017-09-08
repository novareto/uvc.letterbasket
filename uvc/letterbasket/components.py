
import grok
import uvcsite
from .interfaces import IMessage, ILetterBasket


class Message(uvcsite.Content):
    """ Lastschrift Objekt
    """
    grok.name('Lastschrift')
    uvcsite.schema(IMessage)


class LetterBasket(uvcsite.ProductFolder):
    """ Container fr Lastschrift Objekte
    """
    grok.implements(ILetterBasket)
    uvcsite.contenttype(Message)
