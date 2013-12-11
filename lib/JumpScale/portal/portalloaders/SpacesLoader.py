from JumpScale import j
from LoaderBase import LoaderBaseObject, LoaderBase


class Space(LoaderBaseObject):

    def __init__(self):
        LoaderBaseObject.__init__(self, "space")
        self.docprocessor = None

    def loadDocProcessor(self):
        if j.system.fs.exists(j.system.fs.joinPaths(self.model.path, ".macros")):
            # macroPathsPreprocessor = ["system/system__contentmanager/macros/preprocess", j.system.fs.joinPaths(self.model.path, ".macros", "preprocess")]
            # macroPathsWiki = ["system/system__contentmanager/macros/wiki", j.system.fs.joinPaths(self.model.path, ".macros", "wiki")]
            # macroPathsPage = ["system/system__contentmanager/macros/page", j.system.fs.joinPaths(self.model.path, ".macros", "page")]

            #load the macro's only relevant to the space, the generic ones are loaded on docpreprocessorlevel
            macroPathsPreprocessor = [j.system.fs.joinPaths(self.model.path, ".macros", "preprocess")]
            macroPathsWiki = [j.system.fs.joinPaths(self.model.path, ".macros", "wiki")]
            macroPathsPage = [j.system.fs.joinPaths(self.model.path, ".macros", "page")]

            MacroExecutorPreprocess, MacroExecutorPage, MacroExecutorWiki = j.web.geventws.getMacroExecutors()
            spaceMacroexecutorPreprocessor = MacroExecutorPreprocess(macroPathsPreprocessor)
            spaceMacroexecutorPage = MacroExecutorPage(macroPathsPage)
            spaceMacroexecutorWiki = MacroExecutorWiki(macroPathsWiki)
            self.docprocessor = j.tools.docpreprocessor.get(contentDirs=[self.model.path], spacename=self.model.id,
                                                            spaceMacroexecutorPreprocessor=spaceMacroexecutorPreprocessor,
                                                            spaceMacroexecutorPage=spaceMacroexecutorPage,
                                                            spaceMacroexecutorWiki=spaceMacroexecutorWiki)            

        else:
            self.docprocessor = j.tools.docpreprocessor.get(contentDirs=[self.model.path], spacename=self.model.id)

    def createDefaults(self, path):
        self._createDefaults(path, ["default.wiki", "nav.wiki", "notfound.wiki", "template.wiki", "users.cfg"])

    def createDefaultDir(self):

        def callbackForMatchDir(path, arg):
            dirname = j.system.fs.getDirName(path, lastOnly=True)
            if dirname.find(".space") == 0:
                return False
            l = len(j.system.fs.listFilesInDir(path))
            if l > 0:
                return False
            return True

        def callbackFunctionDir(path, arg):
            dirname = j.system.fs.getDirName(path, lastOnly=True)
            if dirname.find(".macros") == 0:
                return  # will not do anything but recursing will still happen
            print "NOTIFY NEW DIR %s IN SPACE %s" % (path, self.model.id)
            j.apps.system.contentmanager.notifySpaceNewDir(self.model.id, self.model.path, path)
            return True

        j.system.fswalker.walkFunctional(self.model.path, callbackFunctionFile=None, callbackFunctionDir=callbackFunctionDir, arg=self.model,
                                         callbackForMatchDir=callbackForMatchDir, callbackForMatchFile=False)  # false means will not process files

    def loadFromDisk(self, path, reset=False):
        self._loadFromDisk(path, reset=False)
        self.createDefaultDir()

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
