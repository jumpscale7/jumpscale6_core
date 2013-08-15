from OpenWizzy import o

class PerformanceTraceFactory():
    """
    """
    
    def profile(self,methodstatement, locals,globals={}):
        """
        create a wrapper method which has no args and then pass that wrapper method to this method as first arg
        method is passed as a string e.g. 'listDirTest()'
        it remove stats is False the path where the stats are will be returned
        make sure that whatever arguments used in the statement are passed to the globals

        example:

        locals={}
        locals["params"]=params
        locals["q"]=q
        do=o.tools.performancetrace.profile('o.apps.system.infomgr.extensions.infomgr.addInfo(params.info)', locals)
        
        """
        import cProfile
        import pstats
        path=o.system.fs.joinPaths(o.dirs.tmpDir,"perftest","%s.log"%o.base.idgenerator.generateRandomInt(1,10000))        
        o.system.fs.createDir(o.system.fs.joinPaths(o.dirs.tmpDir,"perftest"))        
        globs = {
            '__file__': "afile",
            '__name__': '__main__',
            '__package__': None,
        }
        globals.update(globs)
        cProfile.runctx(methodstatement, globals, locals, path)
        p1 = pstats.Stats(path)
        p1.strip_dirs().sort_stats('cum').print_stats(100)
        p1.strip_dirs().sort_stats('time').print_stats(100)
        o.system.fs.removeDirTree(path)




