#!/usr/bin/env python
from ConfigParser import ConfigParser

tmp = """
from OpenWizzy import o
o.base.loader.makeAvailable(o, '%(location)s')

from .%(modulename)s import %(classname)s
o.%(location)s.%(hook)s = %(classname)s()

"""

cfg = ConfigParser()
cfg.read('extension.cfg')
imports = ["from OpenWizzy import o"]
available = set()
data = list()
for section in cfg.sections():
    location = cfg.get(section, 'qlocation')
    classname = cfg.get(section, 'classname')
    modulename = cfg.get(section, 'modulename')
    locationparts = location.split(".")
    imports.append("from .%s import %s" % (modulename, classname) )
    available.add(".".join(locationparts[1:-1]))
    data.append("o.%s = %s()" % (".".join(locationparts[1:]), classname))

data.append("")
result = imports + [ "o.base.loader.makeAvailable(o, '%s')" % x for x in available ] + data
with open('__init__.py', 'w') as fd:
    fd.write("\n".join(result))


