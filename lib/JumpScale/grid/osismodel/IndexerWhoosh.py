from JumpScale import j
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser


class IndexerWhoosh:

    def __init__(self, name):

        if j.system.platformtype.isLinux():
            path = j.system.fs.joinPaths(j.dirs.baseDir, "lib", "python2.7", "site-packages", "whoosh")
            if not j.system.fs.exists(path):  # @todo use ext dir pm_extensionpath property
                j.system.fs.symlink("/opt/qbase6/lib/jumpscaleextensions/core/osis/whoosh", path)

        self.appname, self.actorname, self.modelname = name.split("_")
        self.indexdef = j.core.codegenerator.getClassWhoosh(self.appname, self.actorname, self.modelname)()
        indexpath = j.system.fs.joinPaths(j.dirs.varDir, "index", name)
        self.indexpath = indexpath
        self._init()

    def _init(self):
        if j.system.fs.exists(self.indexpath):
            self.index = open_dir(self.indexpath)
        else:
            j.system.fs.createDir(self.indexpath)
            self.index = create_in(self.indexpath, self.indexdef.getSchema())

        self.queryparser = QueryParser("content", schema=self.indexdef.getSchema())

    def destroy(self):
        j.system.fs.removeDirTree(self.indexpath)
        self._init()

    def rebuild(self):
        self.destroy()
        j.core.osis.rebuildindex(self.appname, self.actorname, self.modelname)

    def addObject(self, obj):
        writer = self.index.writer()
        result = self.indexdef.getIndexArgs(obj)
        for kwargs in result:
            writer.add_document(**kwargs)
        writer.commit(merge=False)

    def addIndexContent(self, indexcontent):
        writer = self.index.writer()
        try:
            writer.add_document(**indexcontent)
            writer.commit(merge=False)
        except Exception, e:
            if str(e).find("No field named") == 0:
                print "index is probably broken, recreate for %s %s %s" % (self.appname, self.actorname, self.modelname)
                writer.cancel()
                self.rebuild()
            else:
                j.errorconditionhandler.processPythonExceptionObject(e)

    def optimize(self):
        # writer=self.index.writer()
        # writer.commit(optimize=True)
        self.index.optimize()

    def delete(self, id):
        self.index.delete_by_term("id", str(id))
        self.index.writer().commit()

    def find(self, querystr):
        query = self.queryparser.parse(unicode(querystr))
        searcher = self.index.searcher()
        result = searcher.search(query, limit=None)
        if result.estimated_length() == 0:
            return []
        fields = result.fields(0).keys()
        result2 = []
        for x in range(result.estimated_length()):
            result2.append(result.fields(x))

        return result2


# class IndexerWhoosh:
    #"""
    #"""


    # def destroyindex(self,name=""):
        # if name<>"":
            # names=[name]
        # else:
            # names=self.indexers.keys()

        # for name in names:
            # indexer=self._getIndexer(name)
            # indexer.destroy()
            # self.indexers.pop(name)

    # def _getIndexer(self,name):
        # if not self.indexers.has_key(name):
            # self.indexers[name]=IndexerWhooshInstance(name)
        # return self.indexers[name]


    # def optimize(self,name):
        # indexer=self._getIndexer(name)
        # indexer.optimize()

    # def find(self,name,query):
        # indexer=self._getIndexer(name)
        # return indexer.find(query)
