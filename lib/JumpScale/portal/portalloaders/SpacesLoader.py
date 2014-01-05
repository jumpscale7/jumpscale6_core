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
