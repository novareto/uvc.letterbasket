# -*- coding: utf-8 -*-

import grok
import json
import time

from base64 import b64encode, b64decode
from datetime import datetime, timedelta
from os import path, makedirs, chmod
from urllib import quote_plus, unquote_plus

from zope.pluggableauth import interfaces
from zope.interface import implementer
from zope.pluggableauth.factories import PrincipalInfo
from Crypto.PublicKey import RSA
from zope.app.appsetup.product import getProductConfiguration


config = getProductConfiguration('keys')
pubkey = config['pubkey']
privkey = config['privkey']


def rsa_pair(pvt_path, pub_path):

    priv = path.isfile(pvt_path)
    pub = path.isfile(pub_path)

    if not priv or not pub:  # IMPORTANT : We override the existing one.

        container = path.dirname(pvt_path)
        if not path.isdir(container):
            makedirs(container)

        container = path.dirname(pub_path)
        if not path.isdir(container):
            makedirs(container)

        key = RSA.generate(2048)

        with open(pvt_path, 'wb') as fd:
            chmod(pvt_path, 0600)
            fd.write(key.exportKey('PEM'))

        pubkey = key.publickey()
        with open(pub_path, 'wb') as fd:
            fd.write(pubkey.exportKey('PEM'))


def load_key(private, public):
    rsa_pair(private, public)
    with open(private, 'rb') as fd:
        priv_key = RSA.importKey(fd.read())

    with open(private, 'rb') as fd:
        pub_key = RSA.importKey(fd.read())

    return priv_key, pub_key


def make_token():
    priv_key, pub_key = load_key(
        privkey, pubkey)

    ts = int(time.mktime((datetime.now() + timedelta(days=10)).timetuple()))
    token = json.dumps({
        'timestamp': ts,
        'id': 'servicetelefon',
    })

    encrypted = pub_key.encrypt(token, 32)
    access_token = quote_plus(b64encode(encrypted[0]))
    return access_token


@implementer(interfaces.IAuthenticatorPlugin)
class TokenAuthenticator(object):

    prefix = 'token.principals.'

    def authenticateCredentials(self, credentials):
        if not credentials:
            return
        access_token = credentials.get('access_token')
        if access_token is None:
            return

        try:
            token = b64decode(access_token)
            priv_key, pub_key = load_key(
                privkey, pubkey)
            decrypted = priv_key.decrypt((token,))
            data = json.loads(decrypted)
        except TypeError:
            return None
        except Exception as exc:
            print exc  # log this nasty error
            return None

        now = int(time.time())

        if now > data['timestamp']:
            # expired
            return None

        authenticated = dict(
                id=data['id'] + '-0',
                title='Token generated',
                description='Token generated',
                login=data['id'] + '-0')
        return PrincipalInfo(**authenticated)

    def principalInfo(self, id):
        """we don´t need this method"""
        if id.startswith('uvc.'):
            return PrincipalInfo(id, id, id, id)


grok.global_utility(TokenAuthenticator, name="token_auth")
from uvcsite.auth.token import TokensCredentialsPlugin
grok.global_utility(TokensCredentialsPlugin, name="token_creds")
