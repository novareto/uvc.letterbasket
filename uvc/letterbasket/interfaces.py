from zope import schema
from zope import interface


class ILetterBasket(interface.Interface):
    pass


class IMessage(interface.Interface):

    title = schema.TextLine(
        title=u"Title",
        description=u"Please give a Title"
        )

    subject = schema.TextLine(
        title=u"Subject",
        description=u"Please provide a Subject"
        )

    message = schema.TextLine(
        title=u"Message",
        description=u"Please provide a Message"
        )

#    attachement = schema.File(
#        title=u"Attachment",
#        description=u"Please provide a Description"
 #       )
