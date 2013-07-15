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
output = ["from OpenWizzy import o"]
for section in cfg.sections():
    location = cfg.get(section, 'qlocation')
    classname = cfg.get(section, 'classname')
    modulename = cfg.get(section, 'modulename')
    locationparts = location.split(".")
    output.insert(1, "from .%s import %s" % (modulename, classname) )
    output.append("o.base.loader.makeAvailable(o, '%s')" % ".".join(locationparts[1:-1] ))
    output.append("o.%s = %s()" % (".".join(locationparts[1:]), classname))

output.append("")
with open('__init__.py', 'w') as fd:
    fd.write("\n".join(output))


