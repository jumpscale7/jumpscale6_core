
from .GeventWebserver import GeventWebserver
from .GeventWebserverClient import GeventWebserverClient
from MacroExecutor import MacroExecutorPage, MacroExecutorWiki, MacroExecutorPreprocess
from .GeventWebserverAuthenticator import GeventWebserverAuthenticator

class GeventWebserverFactory:

    def get(self, port, wwwroot="", filesroot="", cfgdir="",secret=None,admingroups=[]):
        return GeventWebserver(port, wwwroot=wwwroot, filesroot=filesroot, cfgdir=cfgdir,secret=secret)

    def getClient(self, ip, port, secret):
        return GeventWebserverClient(ip, port, secret)

    def getMacroExecutors(self):
        return (MacroExecutorPreprocess, MacroExecutorPage, MacroExecutorWiki)

    def getAuthenticator(self):
        return GeventWebserverAuthenticator()