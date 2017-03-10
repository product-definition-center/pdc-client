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


# copied from py2.7 functools module
def _total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    convert = {
        '__lt__': [('__gt__', lambda self, other: not (self < other or self == other)),
                   ('__le__', lambda self, other: self < other or self == other),
                   ('__ge__', lambda self, other: not self < other)],
        '__le__': [('__ge__', lambda self, other: not self <= other or self == other),
                   ('__lt__', lambda self, other: self <= other and not self == other),
                   ('__gt__', lambda self, other: not self <= other)],
        '__gt__': [('__lt__', lambda self, other: not (self > other or self == other)),
                   ('__ge__', lambda self, other: self > other or self == other),
                   ('__le__', lambda self, other: not self > other)],
        '__ge__': [('__le__', lambda self, other: (not self >= other) or self == other),
                   ('__gt__', lambda self, other: self >= other and not self == other),
                   ('__lt__', lambda self, other: not self >= other)]
    }
    roots = set(dir(cls)) & set(convert)
    if not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
    for opname, opfunc in convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            opfunc.__doc__ = getattr(int, opname).__doc__
            setattr(cls, opname, opfunc)
    return cls


if sys.version_info >= (2, 7):
    from functools import total_ordering
else:
    total_ordering = _total_ordering
