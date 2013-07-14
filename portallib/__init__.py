#load dependencies
from OpenWizzy import o
import OpenWizzy.baselib.key_value_store
import OpenWizzy.baselib.taskletengine
import OpenWizzy.baselib.specparser

o.base.loader.makeAvailable(o, 'manage')
o.base.loader.makeAvailable(o, 'core')
o.base.loader.makeAvailable(o, 'web')
o.base.loader.makeAvailable(o, 'tools')

from .portalcore.PortalManage import PortalManage
from .portalcore.PortalFactory import PortalClientFactory
from .portalloaders.PortalLoaderFactory import PortalLoaderFactory
from .geventWebserver.GeventWebserver import GeventWebserverFactory
from .docgenerator.Docgenerator import DocgeneratorFactory
from .html.HtmlFactory import HtmlFactory
from .docpreprocessor.DocPreprocessorFactory import DocPreprocessorFactory
from .docpreprocessor.DocParser import DocParser
import codegentools
o.manage.portal = PortalManage()
o.core.portal = PortalClientFactory()
o.core.portalloader = PortalLoaderFactory()
o.web.geventws = GeventWebserverFactory()
o.html = HtmlFactory()
o.tools.docgenerator = DocgeneratorFactory()
o.tools.docpreprocessor = DocPreprocessorFactory()
o.tools.docpreprocessorparser = DocParser()
