from OpenWizzy import o
from REGEXTOOL import *
from FS import *

class FSWalker():

    # def _checkDepth(path,depths,root=""):
    #     if depths==[]:
    #         return True
    #     #path=o.system.fs.pathclean(path)
    #     path=self.pathRemoveDirPart(path,root)
    #     for depth in depths:
    #         dname=os.path.dirname(path)
    #         split=dname.split(os.sep)
    #         split = [ item for item in split if item<>""]
    #         #print split
    #         if depth==len(split):
    #             return True
    #     else:
    #         return False

    def __init__(self):
        self.dos=[]

    def log(self,msg):
        print msg

    def registerChange(self,do,ttype,status,name):
        # print "CHANGE: %s %s %s" %(name,ttype,status)
        if len(self.dos)==0:
            self.dos.append(do)
        elif self.dos[-1]<>do:
            self.dos.append(do)
    
    def _findhelper(self,arg,path):
        arg.append(path)
    
    def find(self,root, includeFolders=False,includeLinks=False, pathRegexIncludes=[],pathRegexExcludes=[], contentRegexIncludes=[], contentRegexExcludes=[],followlinks=False):
        """
        @return {files:[],dirs:[],links:[]}
        """

        files=[]
        dirs=[]
        links=[]

        def processfile(path):
            files.append(path)    

        def processdir(path):
            dirs.append(path)    

        def processlink(path):
            links.append(path)   

        matchfile=None

        if pathRegexIncludes<>[] or pathRegexExcludes<>[]:
            if contentRegexIncludes==[] and contentRegexExcludes==[]:
                def matchfile(path):
                    return REGEXTOOL.matchPath(path,pathRegexIncludes,pathRegexExcludes)
            else:
                def matchfile(path):
                    return REGEXTOOL.matchPath(path,pathRegexIncludes,pathRegexExcludes) and REGEXTOOL.matchContent(path,contentRegexIncludes,contentRegexExcludes)

        matchdir=None
        matchlink=None

        if includeFolders:
            if pathRegexIncludes<>[] or pathRegexExcludes<>[]:
                def matchdir(path):
                    return REGEXTOOL.matchPath(path,pathRegexIncludes,pathRegexExcludes)

        if includeLinks:
            if pathRegexIncludes<>[] or pathRegexExcludes<>[]:
                def matchlink(path):
                    return REGEXTOOL.matchPath(path,pathRegexIncludes,pathRegexExcludes)
        
        self.walk(root,callbackFunctionFile=processfile, callbackFunctionDir=processdir,callbackFunctionLink=processlink,args={}, \
            callbackForMatchFile=matchfile,callbackForMatchDir=matchdir,callbackForMatchLink=matchlink,matchargs={},followlinks=followlinks)

        listfiles={}
        listfiles["files"]=files
        listfiles["dirs"]=dirs
        listfiles["links"]=links

        return listfiles
          
    def walk(self,root,callbackFunctionFile=None, callbackFunctionDir=None,callbackFunctionLink=None,args={},callbackForMatchFile=None,callbackForMatchDir=None,callbackForMatchLink=None,matchargs={},followlinks=False):
        '''Walk through filesystem and execute a method per file and dirname

        Walk through all files and folders starting at C{root}, recursive by
        default, calling a given callback with a provided argument and file
        path for every file & dir we could find.

        To match the function use the callbackForMatch function which are separate for dir or file
        when it returns True the path will be further processed
        when None (function not given match will not be done)

        Examples
        ========
        >>> def my_print(path,arg):
        ...     print arg, path
        ...
        #if return False for callbackFunctionDir then recurse will not happen for that dir

        >>> def matchDirOrFile(path,arg):
        ...     return True #means will match all
        ...

        >>> self.walkFunctional('/foo', my_print,my_print, 'test:',matchDirOrFile,matchDirOrFile)
        test: /foo/file1
        test: /foo/file2
        test: /foo/file3
        test: /foo/bar/file4

        @param root: Filesystem root to crawl (string)
        #@todo complete
        
        '''
        #We want to work with full paths, even if a non-absolute path is provided
        root = os.path.abspath(root)

        if not o.base.fs.isDir(root):
            raise ValueError('Root path for walk should be a folder')
        
        # print "ROOT OF WALKER:%s"%root

        self._walkFunctional(root,callbackFunctionFile, callbackFunctionDir,callbackFunctionLink,args, callbackForMatchFile,callbackForMatchDir,callbackForMatchLink,matchargs,followlinks=followlinks)

    def _walkFunctional(self,path,callbackFunctionFile=None, callbackFunctionDir=None,callbackFunctionLink=None,args={}, callbackForMatchFile=None,callbackForMatchDir=None,callbackForMatchLink=None,matchargs={},\
            followlinks=False,dirObjectProcess=True):
        if dirObjectProcess:
            do=o.base.fsobjects.getOWFSDir(path,parent="parent")
        else:
            do=None

        paths=FS.list(path)
        for path2 in paths:
            # self.log("walker path:%s"% path2)
            if o.base.fs.isFile(path2,False):
                # self.log("walker filepath:%s"% path2)
                if callbackForMatchFile==None or callbackForMatchFile(path2,**matchargs):
                    if do<>None:
                        do.registerFile(path2,self)
                    #execute 
                    if callbackFunctionFile<>None:
                        callbackFunctionFile(path2,**args)
                elif callbackForMatchFile==False:                    
                    continue
            elif o.base.fs.isDir(path2, followlinks):
                # self.log("walker dirpath:%s"% path2)
                if callbackForMatchDir==None or callbackForMatchDir(path2,**matchargs):
                    if do<>None:
                        do.registerDir(path2,self)
                    #recurse
                    # print "walker matchdir:%s"% path2
                    if callbackFunctionDir<>None:
                        callbackFunctionDir(path2,**args)
                elif callbackForMatchDir==False:
                    continue                        
                self._walkFunctional(path2,callbackFunctionFile, callbackFunctionDir,callbackFunctionLink,args, callbackForMatchFile,callbackForMatchDir,callbackForMatchLink)
            elif o.base.fs.isLink(path2):
                # self.log( "walker link:%s"% path2)
                if callbackForMatchLink==None or callbackForMatchLink(path2,**matchargs):
                    if do<>None:
                        do.registerLink(path2,self)
                if callbackFunctionLink<>None:
                    #execute 
                    callbackFunctionLink(path2,**args)
                elif callbackFunctionLink==False:
                    continue
        

class FSWalkerFactory():
    def get(self):
        return FSWalker()

o.base.fswalker=FSWalkerFactory()

