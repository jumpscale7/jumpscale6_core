from JumpScale import j
from LoaderBase import LoaderBaseObject, LoaderBase


class Space(LoaderBaseObject):

    def __init__(self):
        LoaderBaseObject.__init__(self, "space")
        self.docprocessor = None
        self._loading = False

    def loadDocProcessor(self,force=False):
        if self._loading and force==False:
            return
        self._loading = True
        self.createDefaultDir()        
        if j.system.fs.exists(j.system.fs.joinPaths(self.model.path, ".macros")):
            #load the macro's only relevant to the space, the generic ones are loaded on docpreprocessorlevel
            macroPathsPreprocessor = [j.system.fs.joinPaths(self.model.path, ".macros", "preprocess")]
            macroPathsWiki = [j.system.fs.joinPaths(self.model.path, ".macros", "wiki")]
            macroPathsPage = [j.system.fs.joinPaths(self.model.path, ".macros", "page")]

            name = self.model.id.lower()
            webserver = j.core.portal.active
            webserver.macroexecutorPage.addMacros(macroPathsPage, name)
            webserver.macroexecutorPreprocessor.addMacros(macroPathsPreprocessor, name)
            webserver.macroexecutorWiki.addMacros(macroPathsWiki, name)

            
        self.docprocessor = j.tools.docpreprocessor.get(contentDirs=[self.model.path], spacename=self.model.id)
        

    def createDefaults(self, path):
        self._createDefaults(path)

    def createDefaultDir(self):

        def callbackForMatchDir(path, arg):
            dirname = j.system.fs.getDirName(path+"/", lastOnly=True)
            if dirname.find(".") == 0:
                return False
            # l = len(j.system.fs.listFilesInDir(path))
            # if l > 0:
            #     return False
            return True

        def callbackFunctionDir(path, arg):
            dirname = j.system.fs.getDirName(path+"/", lastOnly=True)
            dirname = j.system.fs.getDirName(path+"/", lastOnly=True)

            if not j.system.fs.exists(j.system.fs.joinPaths(path,"%s.wiki"%dirname)):
                dirnamel=dirname.lower()
                for item in  j.system.fs.listFilesInDir(path):
                    item= j.system.fs.getDirName(item+"/", lastOnly=True)
                    item=item.lower()
                    item=item.replace(".wiki","")
                    print item
                    if item==dirnamel:
                        return
                
                source = j.system.fs.joinPaths(self.model.path, ".space", "template.wiki")
                dest= j.system.fs.joinPaths(path,"%s.wiki"%dirname)
                j.system.fs.copyFile(source, dest)

                print "NOTIFY NEW DIR %s IN SPACE %s" % (path, self.model.id)
            
            return True

        j.system.fswalker.walkFunctional(self.model.path, callbackFunctionFile=None, callbackFunctionDir=callbackFunctionDir, arg=self.model,
                                         callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=False)  # false means will not process files

    def loadFromDisk(self, path, reset=False):
        self._loadFromDisk(path, reset=False)        

    def reset(self):
        self.docprocessor = None
        self.loadFromDisk(self.model.path, reset=True)


class SpacesLoader(LoaderBase):

    def __init__(self):
        """
        """
        LoaderBase.__init__(self, "space", Space)
        self.macrospath = ""
        self.spaceIdToSpace = self.id2object
        self.getSpaceFromId = self.getLoaderFromId
