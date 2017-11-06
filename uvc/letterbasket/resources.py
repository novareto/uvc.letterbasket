# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2011 NovaReto GmbH

import grok
from fanstatic import Library, Resource

library = Library('uvc.letterbasket', 'static')
threadcss = Resource(library, 'main.css')
