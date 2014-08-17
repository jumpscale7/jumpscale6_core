
from JumpScale import j
from Confluence2HTML import Confluence2HTML
from Confluence2RST import Confluence2RST


class DocgeneratorFactory:

    def __init__(self):
        pass

    def getConfluenceClient(self, url, login, passwd, spacename, erasespace=False, erasepages=False):
        """
        @param url e.g. http://10.0.1.193:8080/confluence
        """
        from core.Docgenerator.WikiClientConfluence import WikiClientConfluence
        if url != "":
            j.clients.confluence.connect(url, login, passwd)
        return WikiClientConfluence(spacename, erasespace, erasepages)

    # def getAlkiraClient(self,url,login,passwd,spacename,erasespace=False,erasepages=False):
        #"""
        #@param url e.g. http://10.0.1.193:8080/confluence
        #"""
        # @todo P1
        #from core.Docgenerator.WikiClientAlkira import WikiClientAlkira
        # return WikiClientAlkira(spacename,erasespace,erasepages)

    def convertConfluenceToRST(self,src,dest):
        convertor=self.getConfluence2rstConvertor()
        # j.system.fs.removeDirTree(dest)
        for path in j.system.fs.listFilesInDir(src,True,filter="*.wiki"):
            if path.find(".space")<>-1 or path.find(".files")<>-1:
                continue
            if j.system.fs.getBaseName(path)[0]=="_":
                continue
            print "process:%s"%path
            indest=j.system.fs.pathRemoveDirPart(path,src)
            dest2="%s/%s"%(dest,indest)
            C=j.system.fs.fileGetContents(path)
            C2=convertor.convert(C)
            if C2=="":
                continue
            ddir=j.system.fs.getDirName(dest2)
            j.system.fs.createDir(ddir)
            
            basename=j.system.fs.getBaseName(path)
            basename=basename.replace(".wiki",".rst")

            dest3=j.system.fs.joinPaths(ddir,basename)
            print "dest:%s"%dest3
            j.system.fs.writeFile(filename=dest3,contents=str(C2))

        for path in j.system.fs.listFilesInDir(src,True,filter="*.rst"):
            indest=j.system.fs.pathRemoveDirPart(path,src)
            dest2="%s/%s"%(dest,indest)
            C=j.system.fs.fileGetContents(path)
            ddir=j.system.fs.getDirName(dest2)
            j.system.fs.createDir(ddir)            
            basename=j.system.fs.getBaseName(path)
            dest3=j.system.fs.joinPaths(ddir,basename)
            j.system.fs.writeFile(filename=dest3,contents=str(C))

    def getConfluence2htmlConvertor(self):
        return Confluence2HTML()

    def getConfluence2rstConvertor(self):
        return Confluence2RST()        

    def pageNewConfluence(self, pagename, parent="Home"):
        from core.docgenerator.PageConfluence import PageConfluence
        page = PageConfluence(pagename, content="", parent=parent)
        return page

    # def pageNewAlkira(self,pagename,parent="Home",):
        #from core.Docgenerator.PageAlkira import PageAlkira
        # page=PageAlkira(pagename,content="",parent=parent)
        # return page

    def pageNewHTML(self, pagename, htmllibPath=None):
        from JumpScale.portal.docgenerator.PageHTML import PageHTML
        page = PageHTML(pagename, htmllibPath=htmllibPath)
        return page

    def pageNewRST(self, pagename, htmllibPath=None):
        from JumpScale.portal.docgenerator.PageRST import PageRST
        page = PageRST(pagename)
        return page

    def pageGroupNew(self, pages={}):
        from core.docgenerator.PageGroup import PageGroup
        return PageGroup(pages)

    def getMacroPath(self):
        dirname = j.system.fs.getDirName(__file__)
        return j.system.fs.joinPaths(dirname, 'macros')
    # def convertConfluenceFileToPage(self,confluenceFilePath,pageOut,dirPathOut=""):
        #"""
        #@param confluenceFilePath is path of confluence file, the files required by that file need to be in same dir
        #@param pageOut is the page in which we are going to insert the doc statements e.g. addnewline, ...
        #"""
        # if dirPathOut=="":
            # dirPathOut=j.system.fs.getDirName(confluenceFilePath)
        # cc=ConfluenceConverter()
        # return cc.convert(pageOut,confluenceFilePath,dirPathOut)
