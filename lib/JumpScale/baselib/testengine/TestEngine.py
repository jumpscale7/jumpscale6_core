import sys
from JumpScale import j
import imp
import JumpScale.grid.osis
import inspect

class FileLikeStreamObject(object):
    def __init__(self):
        self.out=""

    def write(self, buf,**args):
        for line in buf.rstrip().splitlines():
            #print "###%s"%line
            self.out+="%s\n"%line

 

class Test():
    def __init__(self,db,testclass):
        self.db=db
        self.testclass=None
        self.eco=None

    def execute(self,testrunname,debug=False):

        def testDebug(code):
            return self.db.source[name].find("import ipdb")<>-1 or self.db.source[name].find("import embed")<>-1

        self.testclass.setUp()
        print "\n##TEST:%s %s"%(self.db.organization,self.db.name)
        print self.db.path
        for test in inspect.getmembers(self.testclass):
            if str(test[0]).find("test_")==0:
                #found test
                name=test[0][5:]
                print "execute test:%-30s"%name,

                out=FileLikeStreamObject()

                sysstdout=sys.stdout
                sysstderr=sys.stderr

                if testDebug(self.db.source[name])==False:            
                    sys.stdout = out
                    sys.stderr = out
                
                try:
                    self.db.result=test[1]()
                except Exception,e:
                    print "ERROR IN TEST:"
                    print out.out
                    sys.stdout =sysstdout
                    sys.stderr =sysstderr  
                    eco=j.errorconditionhandler.parsePythonErrorObject(e)
                    eco.tags="testrunner testrun:%s org:%s testgroup:%s testname:%s testpath:%s" % (self.db.testrun,\
                            self.db.organization, self.db.name,name,self.db.path)
                    j.errorconditionhandler.processErrorConditionObject(eco)                    
                    if debug:
                        sys.exit()
                sys.stdout =sysstdout
                sys.stderr =sysstderr
                print "ok"
                self.db.output[name]=out.out
        try:
            self.testclass.tearDown()
        except Exception,e:
            pass

    def __str__(self):
        out=""
        for key,val in self.db.__dict__.iteritems():
            if key[0]<>"_" and key not in ["source","output"]:
                out+="%-35s :  %s\n"%(key,val)
        items=out.split("\n")
        items.sort()
        return "\n".join(items)

    __repr__ = __str__




class TestEngine():
    def __init__(self):
        self.paths=[]
        self.tests=[]
        self.outputpath="/opt/jumpscale/apps/gridportal/base/Tests/TestRuns/"

    def initTests(self,osisip="127.0.0.1",login="",passwd=""): #@todo implement remote osis
        client = j.core.osis.getClient()
        self.osis=j.core.osis.getClientForCategory(client, 'system', 'test')


    def runTests(self,testrunname=None,debug=False):

        if testrunname==None:
            testrunname=j.base.time.getLocalTimeHRForFilesystem()

        for path in self.paths:
            print "scan dir: %s"%path
            for item in j.system.fs.listFilesInDir(path,filter="*__test.py",recursive=True):
                testdb=self.osis.new()
                name=j.system.fs.getBaseName(item).replace("__test.py","").lower()
                testmod = imp.load_source(name, item)
                testclass=testmod.TEST()

                test=Test(testdb,testclass)

                test.db.author=testmod.author
                test.db.descr=testmod.descr.strip()
                test.db.organization=testmod.organization
                test.db.version=testmod.version
                test.db.categories=testmod.category.split(",")
                test.db.enable=testmod.enable
                test.db.license=testmod.license
                test.db.priority=testmod.priority
                test.db.gid=j.application.whoAmI.gid
                test.db.nid=j.application.whoAmI.nid
                test.db.state="INIT"
                test.db.testrun=testrunname
                test.db.name=name
                test.db.path=item
                test.db.priority=testmod.priority
                test.db.id=0

                C=j.system.fs.fileGetContents(item)
                methods=j.codetools.regex.extractBlocks(C,["def test"])
                for method in methods:
                    methodname=method.split("\n")[0][len("    def test_"):].split("(")[0]
                    methodsource="\n".join([item.strip() for item in method.split("\n")[1:] if item.strip()<>""])
                    test.db.source[methodname]=methodsource

                test.testclass=testclass
                self.osis.set(test.db)
                self.tests.append(test)

        priority={}
        for test in self.tests:
            if not priority.has_key(test.db.priority):
                priority[test.db.priority]=[]    
            priority[test.db.priority].append(test)
        prio=priority.keys()
        prio.sort()
        for key in prio:
            for test in priority[key]:
                #now sorted
                test.execute(testrunname=testrunname,debug=debug)
                self.osis.set(test.db)



                
