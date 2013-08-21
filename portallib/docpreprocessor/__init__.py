from OpenWizzy import o
from .DocPreprocessorFactory import DocPreprocessorFactory
from .DocParser import DocParser
o.base.loader.makeAvailable(o, 'tools')
o.tools.docpreprocessor = DocPreprocessorFactory()
o.tools.docpreprocessorparser = DocParser()
