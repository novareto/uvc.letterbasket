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
