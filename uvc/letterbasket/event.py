#!/usr/bin/env python
# -*- coding: utf-8 -*-

import grok
import uvcsite
import tempfile
import transaction
import unicodedata

from grokcore.message import send
from hurry.workflow.interfaces import IWorkflowInfo
from uvc.letterbasket.interfaces import IMessage
from uvc.token_auth.plugin import TokenAuthenticationPlugin
from uvcsite.extranetmembership.interfaces import IUserManagement
from uvcsite.utils.mail import send_mail
from zope.component import getUtility


BODY = u"""\
Guten Tag,

die Schule:

%s

%s
%s


hat folgendes Anliegen:

%s

Antworten Sie bitte mit diesem Link: %s

Gegebenenfalls koennen Sie die Mail auch an den entsprechenden Sachbearbeiter weiterleiten.



Vielen Dank

Ihr Schulportal
"""


BODYR = u"""\
Guten Tag,

auf Ihre Anfrage über das Schulportal der Unfallkasse Hessen wurde wie folgt geantwortet:

%s


Um gegebenenfalls auf die Nachricht zu antworten, melden Sie sich bitte im Schulportal an.


Freundliche Grüße

Ihre Unfallkasse Hessen
"""


def getHomeFolder(obj):
    while obj is not None:
        if uvcsite.IMyHomeFolder.providedBy(obj):
            return obj
        obj = obj.__parent__
    raise ValueError("NoHF Found")


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


#@grok.subscribe(IMessage, uvcsite.IAfterSaveEvent)
def handle_save(obj, event, transition='publish'):
    sp = transaction.savepoint()
    try:
        betreff = obj.title
        nachrichtentext = obj.message
        fname = None
        filename = None
        if hasattr(obj.attachment, 'data'):
            ntf = tempfile.NamedTemporaryFile()
            ntf.write(obj.attachment.data)
            ntf.seek(0)
            fname = ntf.name
            filename = obj.attachment.filename
        um = getUtility(IUserManagement)
        link = "%s?form.field.access_token=%s" % (grok.url(event.request, obj, 'add'), TokenAuthenticationPlugin.generate_token())
        link = link.replace('https://schule-login.ukh.de', 'http://10.64.54.12:7787/app')
        f_adr = "schulportal@ukh.de"
        hf = getHomeFolder(obj)
        # Servicetelefon !!!!
        if event.principal.id == "servicetelefon-0":
            f_adr = "ukh@ukh.de"
            body = BODYR % (nachrichtentext)
            antwortto = um.getUser(hf.__name__).get('email').strip()
            to = [antwortto, ]
        # Schule
        #if event.principal.id != "servicetelefon-0":
        else:
            to = ['ukh@ukh.de', ]
            sdat = event.principal.getAdresse()
            adrz1 = sdat['iknam1'].strip() + ' ' + sdat['iknam2'].strip()
            adrz2 = sdat['ikstr'].strip()### + ' ' + sdat['iknam2'].strip()
            adrz3 = str(sdat['enrplz']).strip() + ' ' + sdat['ikhort'].strip()
            body = BODY % (adrz1, adrz2, adrz3, nachrichtentext, link)
        to = ['m.seibert@ukh.de', ]
        filename = remove_accents(filename)
        send_mail(
            f_adr,
            to,
            u"Anfrage Schulportal %s" % betreff,
            #u"Anfrage Schulportal: " + str(betreff),
            body=body,
            file=fname,
            filename=filename
        )
        IWorkflowInfo(obj).fireTransition(transition)
        send(u'Vielen Dank, Ihre Nachricht wurde gesendet.', type='message', name='session')
    except StandardError:
        sp.rollback()
        # IWorkflowInfo(obj).fireTransition('progress')
        uvcsite.logger.exception("Achtung FEHLER")
