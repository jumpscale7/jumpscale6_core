from OpenWizzy import o
from .Docgenerator import DocgeneratorFactory
o.base.loader.makeAvailable(o, 'tools')
o.tools.docgenerator = DocgeneratorFactory()
