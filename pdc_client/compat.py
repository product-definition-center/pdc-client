# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Red Hat
# Licensed under The MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import sys

PY3 = sys.version_info[0] == 3


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


if PY3:
    def iteritems(d, **kw):
        return iter(d.items(**kw))

    string_type = str

else:
    def iteritems(d, **kw):
        return d.iteritems(**kw)

    string_type = basestring
