# -*- coding: utf-8 -*-

import grok
import uvcsite
import hashlib
import json
import time
from datetime import datetime, timedelta

from uvc.layout.forms.event import AfterSaveEvent
from uvcsite.content.views import Add, Edit
from zope.interface import directlyProvides

from .interfaces import IThreadRoot, IMessage, ILetterBasket
from .resources import threadcss


grok.templatedir('templates')


#### THIS IS DEMO VIEW
from uvc.token_auth.plugin import TokenAuthenticationPlugin
from zope.interface import Interface

class Token(grok.View):
    grok.name('token')
    grok.context(Interface)
    grok.require('zope.Public')

    def render(self):
        return TokenAuthenticationPlugin.generate_token()
####


def lineage(node, target):
    if target.providedBy(node):
        return node
    if node.__parent__:
        return lineage(node.__parent__, target)
    raise RuntimeError('Parent could not be found')


class AddThread(Add):
    grok.name('add')
    grok.context(ILetterBasket)

    @property
    def fields(self):
        fields = super(AddThread, self).fields
        fields['access_token'].mode = "hidden"
        return fields

    def create(self, data):
        content = Add.create(self, data)
        directlyProvides(content, IThreadRoot)
        return content

    @uvcsite.action(u'Abbrechen')
    def handle_cancel(self):
        self.flash(u'Die Aktion wurde abgebrochen')
        self.redirect(self.application_url())

    @uvcsite.action(u'Senden', identifier="uvcsite.add")
    def handleAdd(self):
        data, errors = self.extractData()
        if errors:
            self.flash('Es sind Fehler aufgetreten')
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            grok.notify(AfterSaveEvent(obj, self.request))


class AddMessage(Add):
    grok.name('add')
    grok.context(IMessage)

    @property
    def fields(self):
        fields = super(AddMessage, self).fields
        fields['access_token'].mode = "hidden"
        return fields

    def update(self):
        self.thread = lineage(self.context, IThreadRoot)
        Add.update(self)

    def add(self, *args, **kwargs):
        Add.add(self, *args, **kwargs)
        self.thread.count += 1

    def nextURL(self):
        self.flash('Vielen Dank, Ihre Nachricht wurde gesendet.')
        data, errors = self.extractData()
        if 'access_token' in data.keys():
            at = "?form.field.access_token=%s" % make_token()
            print "TURL", self.url(self.thread)  + at
            return self.url(self.thread) + at
        return self.url(self.thread)

    @uvcsite.action(u'Nachricht senden', identifier="uvcsite.add")
    def handleAdd(self):
        data, errors = self.extractData()
        if errors:
            self.flash('Es sind Fehler aufgetreten')
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            grok.notify(AfterSaveEvent(obj, self.request))

    @uvcsite.action(u'Abbrechen')
    def handle_cancel(self):
        self.flash(u'Die Aktion wurde abgebrochen')
        self.redirect(self.application_url())


def read_token(thread, request):
    access_key = request.form.get('token', None)
    if access_key is not None:
        try:
            token = b6decode(unquote(access_key))
            priv_key, pub_key = load_key(
                '/tmp/letterbox.key', '/tmp/letterbox.pub')
            decrypted = priv_key.decrypt(encrypted)
        except TypeError:
            return None
    return None


class EditMessage(Edit):
    grok.context(IMessage)
    grok.require('zope.ManageSite')  # Make it admin only


class MessageRedirect(grok.View):
    grok.name('index')
    grok.context(IMessage)
    grok.require('zope.Public')

    def render(self):
        at = ""
        if 'access_token' in self.request.form.keys():
            at = "?access_token=%s" % self.request.form['access_token']
        return self.redirect(self.url(lineage(self.context, IThreadRoot)) + at)



class MessageDisplay(grok.View):
    grok.name('display')
    grok.context(IMessage)
    grok.require('zope.Public')

    can_answer = True

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

    can_answer = True

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
        return "Sie antworten auf folgende Nachricht: %s" % self.context.message


from uvcsite.content.tables import CheckBoxColumn as CBC
from megrok.z3ctable import CheckBoxColumn


class CheckBox(CBC):
    weight = 0
    grok.context(ILetterBasket)
    grok.name('checkBox')

    def renderCell(self, item):
        return CheckBoxColumn.renderCell(self, item)
