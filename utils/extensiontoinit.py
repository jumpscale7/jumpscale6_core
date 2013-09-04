#!/usr/bin/env python
from ConfigParser import ConfigParser

cfg = ConfigParser()
cfg.read('extension.cfg')
imports = ["from JumpScale import j"]
available = set()
data = list()
for section in cfg.sections():
    location = cfg.get(section, 'qlocation')
    classname = cfg.get(section, 'classname')
    modulename = cfg.get(section, 'modulename')
    locationparts = location.split(".")
    imports.append("from .%s import %s" % (modulename, classname) )
    available.add(".".join(locationparts[1:-1]))
    data.append("j.%s = %s()" % (".".join(locationparts[1:]), classname))

data.append("")
result = imports + [ "j.base.loader.makeAvailable(j, '%s')" % x for x in available ] + data
with open('__init__.py', 'w') as fd:
    fd.write("\n".join(result))


