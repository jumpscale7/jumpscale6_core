
from OpenWizzy import o
from Confluence2HTML import Confluence2HTML

class DocgeneratorFactory:
    def __init__(self):
        pass

    def getConfluenceClient(self,url,login,passwd,spacename,erasespace=False,erasepages=False):
        """
        @param url e.g. http://10.0.1.193:8080/confluence
        """
        from core.Docgenerator.WikiClientConfluence import WikiClientConfluence
        if url<>"":
            o.clients.confluence.connect(url,login,passwd)
        return WikiClientConfluence(spacename,erasespace,erasepages)

    #def getAlkiraClient(self,url,login,passwd,spacename,erasespace=False,erasepages=False):
        #"""
        #@param url e.g. http://10.0.1.193:8080/confluence
        #"""
        ##@todo P1
        #from core.Docgenerator.WikiClientAlkira import WikiClientAlkira
        #return WikiClientAlkira(spacename,erasespace,erasepages)

    def getConfluence2htmlConvertor(self):
        return Confluence2HTML()

    def pageNewConfluence(self,pagename,parent="Home"):
        from core.docgenerator.PageConfluence import PageConfluence	
        page=PageConfluence(pagename,content="",parent=parent)
        return page

    #def pageNewAlkira(self,pagename,parent="Home",):
        #from core.Docgenerator.PageAlkira import PageAlkira
        #page=PageAlkira(pagename,content="",parent=parent)
        #return page
        
    def pageNewHTML(self,pagename,htmllibPath=None):
        from OpenWizzy.portal.docgenerator.PageHTML import PageHTML
        page=PageHTML(pagename,htmllibPath=htmllibPath)
        return page

    def pageGroupNew(self,pages={}):
        from core.docgenerator.PageGroup import PageGroup	
        return PageGroup(pages)
    
    def getMacroPath(self):
        dirname = o.system.fs.getDirName(__file__)
        return o.system.fs.joinPaths(dirname, 'macros')
    #def convertConfluenceFileToPage(self,confluenceFilePath,pageOut,dirPathOut=""):
        #"""
        #@param confluenceFilePath is path of confluence file, the files required by that file need to be in same dir
        #@param pageOut is the page in which we are going to insert the doc statements e.g. addnewline, ...
        #"""
        #if dirPathOut=="":
            #dirPathOut=o.system.fs.getDirName(confluenceFilePath)        
        #cc=ConfluenceConverter()
        #return cc.convert(pageOut,confluenceFilePath,dirPathOut)

