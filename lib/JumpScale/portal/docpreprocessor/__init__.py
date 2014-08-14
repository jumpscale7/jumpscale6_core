from JumpScale import j
from .DocPreprocessorFactory import DocPreprocessorFactory
from .DocParser import DocParser
j.base.loader.makeAvailable(j, 'tools')
j.tools.docpreprocessor = DocPreprocessorFactory()
j.tools.docpreprocessorparser = DocParser()
