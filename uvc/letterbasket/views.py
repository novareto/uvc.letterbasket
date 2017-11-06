# -*- coding: utf-8 -*-

import grok
import uvcsite
import hashlib
from uvcsite.content.views import Add, Edit
from zope.interface import directlyProvides
from .interfaces import IThreadRoot, IMessage, ILetterBasket
from .resources import threadcss


grok.templatedir('templates')


def lineage(node, target):
    if target.providedBy(node):
        return node
    if node.__parent__:
        return lineage(node.__parent__, target)
    raise RuntimeError('Parent could not be found')


class AddThread(Add):
    grok.name('add')
    grok.context(ILetterBasket)

    def create(self, data):
        content = Add.create(self, data)
        directlyProvides(content, IThreadRoot)
        return content


class AddMessage(Add):
    grok.name('add')
    grok.context(IMessage)

    def update(self):
        self.thread = lineage(self.context, IThreadRoot)
        Add.update(self)

    def add(self, *args, **kwargs):
        Add.add(self, *args, **kwargs)
        self.thread.count += 1
        
    def nextURL(self):
        self.flash('Message posted')
        return self.url(self.thread)


class EditMessage(Edit):
    grok.context(IMessage)
    grok.require('zope.ManageSite')  # Make it admin only


class MessageRedirect(grok.View):
    grok.name('index')
    grok.context(IMessage)

    def render(self):
        return self.redirect(self.url(lineage(self.context, IThreadRoot)))


class MessageDisplay(grok.View):
    grok.name('display')
    grok.context(IMessage)

    def update(self):
        self.has_replies = bool(len(self.context))
        self.uri = self.url(self.context)
        self.uid = hashlib.sha1(self.uri).hexdigest()
        attachment = getattr(self.context, 'attachment', None)
        if attachment:
            self.download = "%s/++download++attachment" % self.uri
        else:
            self.download = None

    def display(self, reply):
        view = MessageDisplay(reply, self.request)
        view.update()
        return view()


class ThreadDisplay(uvcsite.Page):
    grok.name('index')
    grok.context(IThreadRoot)

    def update(self):
        threadcss.need()
        self.view = MessageDisplay(self.context, self.request)
        self.view.update()


class ThreadInfo(grok.Viewlet):
    grok.order(600)
    grok.context(IMessage)
    grok.require('uvc.AddContent')
    grok.view(uvcsite.AddForm)
    grok.viewletmanager(uvcsite.IAboveContent)

    def render(self):
        # MAKE ME BETTER
        return "You are answering to the message : %s" % self.context.message
