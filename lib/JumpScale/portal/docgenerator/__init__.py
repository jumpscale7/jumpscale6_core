from JumpScale import j
from .Docgenerator import DocgeneratorFactory
j.base.loader.makeAvailable(j, 'tools')
j.tools.docgenerator = DocgeneratorFactory()
