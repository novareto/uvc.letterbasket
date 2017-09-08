import grok
import uvcsite


class Message(uvcsite.ProductRegistration):
    grok.name('nachrichten')
    grok.title('Nachrichten')
    grok.description('Nachrichten')
    uvcsite.productfolder('uvc.letterbasket.components.LetterBasket')
