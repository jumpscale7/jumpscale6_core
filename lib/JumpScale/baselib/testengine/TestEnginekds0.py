import sys
from JumpScale import j
import imp
import time
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

        print "\n##TEST:%s %s"%(self.db.organization,self.db.name)
<<<<<<< local
        self.testclass.setUp()
        print "setup"
=======
        res = {'total': 0, 'error': 0, 'success': 0, 'failed': 0 }
>>>>>>> other
        self.db.starttime = time.time() 
        print self.db.path
        self.db.state = 'OK'
<<<<<<< local
        for test in inspect.getmembers(self.testclass):
            if str(test[0]).find("test_")==0:
                #found test
                name=test[0][5:]
                print "execute test:%-30s"%name

                out=FileLikeStreamObject()

                try:
                    if debug==False and testDebug(self.db.source[name])==False:            
                        sys.stdout = out
                        sys.stderr = out
                except Exception,e:
                    from IPython import embed
                    print "DEBUG NOW 754"
                    embed()
                    
                
                try:
                    self.db.result[name]=test[1]()
                    self.db.teststates[name] = 'OK'
                except Exception,e:
                    self.db.state = 'ERROR'
=======
        result = TestResult(debug)
        suite = unittest.defaultTestLoader.loadTestsFromModule(self.testmodule)
        suite.run(result)
        for test, buffer in result.tests.iteritems():
            res['total'] += 1
            name = test._testMethodName[5:]
            self.db.output[name]=buffer.getvalue()
            if test in result.errors or test in result.failure:
                if test in result.errors:
                    res['error'] += 1
                    error = result.errors[test]
>>>>>>> other
                    self.db.teststates[name] = 'ERROR'
<<<<<<< local
                    sys.stdout =j.tools.testengine.sysstdout
                    sys.stderr =j.tools.testengine.sysstderr  
                    print "ERROR IN TEST:"
                    print out.out
                    eco=j.errorconditionhandler.parsePythonErrorObject(e)
=======
                    self.db.state = 'ERROR'
                else:
                    res['failed'] += 1
                    error = result.failure[test]
                    self.db.teststates[name] = 'FAILURE'
                    if self.db.state != 'ERROR':
                        self.db.state == 'FAILURE'
                with j.logger.nostdout():
                    eco=j.errorconditionhandler.parsePythonErrorObject(error[1], error[0], error[2])
>>>>>>> other
                    eco.tags="testrunner testrun:%s org:%s testgroup:%s testname:%s testpath:%s" % (self.db.testrun,\
                            self.db.organization, self.db.name,name,self.db.path)
                    j.errorconditionhandler.processErrorConditionObject(eco)
                    self.db.result[name] = eco.guid
<<<<<<< local
                    if debug:
                        sys.exit()
                sys.stdout =j.tools.testengine.sysstdout
                sys.stderr =j.tools.testengine.sysstderr
                print "ok"
                self.db.output[name]=out.out
        try:
            self.testclass.tearDown()
        except Exception,e:
=======
                print "Fail in test %s" % name
                print self.db.output[name]
                print eco
            else:
                res['success'] += 1
                self.db.teststates[name] = 'OK'
>>>>>>> other
            pass
        self.db.endtime = time.time()
<<<<<<< local
=======
        print ''
        return res
>>>>>>> other

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
        self.sysstdout=sys.stdout
        self.sysstderr=sys.stderr  
        self.noOsis=False      

    def initTests(self,osisip="127.0.0.1",login="",passwd=""): #@todo implement remote osis
        client = j.core.osis.getClient(user="root")
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

                if not testmod.enable:
                    continue

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
                test.db.send2osis=getattr(testmod,"send2osis",True)
                test.db.state = 'INIT'
                test.db.teststates = dict()
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
                if not self.noOsis and test.db.send2osis:
                    guid, _, _ = self.osis.set(test.db)
                    test.db.load(self.osis.get(guid).__dict__)
                self.tests.append(test)

        print "all tests loaded in osis"

        priority={}
        for test in self.tests:
            if not priority.has_key(test.db.priority):
                priority[test.db.priority]=[]    
            priority[test.db.priority].append(test)
        prio=priority.keys()
        prio.sort()
        results = list()
        for key in prio:
            for test in priority[key]:
                #now sorted
                # print test
<<<<<<< local
                test.execute(testrunname=testrunname,debug=debug)
                if not self.noOsis and test.db.send2osis:
                    self.osis.set(test.db)
=======
                results.append(test.execute(testrunname=testrunname,debug=debug))
                self.osis.set(test.db)
        total = sum(x['total'] for x in results)
        error = sum(x['error'] for x in results)
        failed = sum(x['failed'] for x in results)
        print "Ran %s tests" % total,
        if error:
            print '%s Error' % error,
        if failed:
            print '%s Failed' % failed,
        print ''

>>>>>>> other



                
