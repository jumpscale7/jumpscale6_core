# To change this template, choose Tools | Templates
# and open the template in the editor.

# Tests are put at the path: /opt/tests
#                            /opt/tests/test1/Test.py
#                            /opt/tests/test1/beforeFiles/...
#                            /opt/tests/test1/afterFiles/...
#

from JumpScale import j

def assertTrue(value):
    if not value:
        raise RuntimeError()

def assertFalse(value):
    if value:
        raise RuntimeError()

def assertEquals(value1, value2):
    if value1 != value2:
        raise RuntimeError('NOT EQUAL:\n value1:  ' + str(value1) + '\n\n value2 :  ' + str(value2))

def assertNotNone(value1):
    if value1 == None:
        raise RuntimeError()

def assertNotEmpty(value1):
    if value1 == []:
        raise RuntimeError("NOT EMPTY: " + str(value1))

def assertEmpty(value1):
    if not value1 == []:
        raise RuntimeError('Not Empty ' + str(value1))

def assertLen(array, size):
    if not len(array) == size:
        raise RuntimeError('Array ' + str(array))
    
def cleanStr(value):
    return value.replace('\n', '').replace('\t', '').replace(' ', '')

def assertStringEquals(value1, value2):
        value1 = str(value1)
        value2 = str(value2)
        assertEquals(cleanStr(value1), cleanStr(value2))

#@todo P1 what is testrunner doing in this dir

class TestRunner:

    # ASSERTS
    # END OF ASSERTS
    
    def loadTestModule(self, testName):
        file = '/opt/testcases/' + testName + '/Test.py'
        import imp
        module = imp.load_source(open(file).read(), file)
        if module == None:
            raise RuntimeError('Could not find file ' + file)
        module.assertTrue = assertTrue
        module.assertEquals = assertEquals
        module.assertStringEquals = assertStringEquals
        module.assertNotEmpty = assertNotEmpty
        module.assertEmpty = assertEmpty
        module.assertNotNone = assertNotNone
        module.assertFalse = assertFalse
        module.assertLen = assertLen
        return module
        
    def beforeFilesInheritFrom(self, testName):
        return self.loadTestModule(testName).beforeFilesInheritFrom

    def afterFilesInheritFrom(self, testName):
        return self.loadTestModule(testName).afterFilesInheritFrom
    
    def doTest(self, testName):
        success = self.doBeforeFiles(testName)
        success = success and self.doScript(testName)
        success = success and self.doAfterFiles(testName)
        success = success and self.doCleanUp(testName)
        return success
        
    def doScript(self, testName):
        try:
            self.loadTestModule(testName).doTest()
            return True
        except Exception, e:
            import sys
            import traceback
            j.console.echo('Script failed for test ' + testName + ' got error:')
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print '\n'.join(traceback.format_exception(exceptionType, exceptionValue,
                                                  exceptionTraceback))
            return False
    
    def doBeforeFiles(self, testName):
        # first copy the files from the common files system
        inheritedTestCase = self.beforeFilesInheritFrom(testName)
        if inheritedTestCase != '':
            self.doBeforeFiles(testName)
        # copy each file to the dir tree
        baseDir = '/opt/testcases/' + testName + '/beforeFiles'
        j.system.fs.copyDirTree(baseDir, '/opt/qbase3/')
        return True

    def doAfterFiles(self, testName):

        # first copy the files from the common files system
        inheritedTestCase = self.afterFilesInheritFrom(testName)
        if inheritedTestCase != '':
            self.doAfterFiles(testName)

        # assert that each file is present and equals the existing files
        baseDir      = '/opt/testcases/' + testName + '/afterFiles'
        files        = j.system.fs.walk(baseDir, recurse=1)
        differences  = []
        
        for file in files:
            projectedFile = '/opt/qbase3' + file[len(baseDir):]
            if not j.system.fs.exists(projectedFile):
                differences += [file]
                continue
            if open(file).read() != open(projectedFile).read():
                differences += [file]
                continue

        if differences:
            j.console.echo('\n\nTests failed for test ' + testName + ', expected different results for :')
            for diff in differences:
                j.console.echo(diff)

        return True

    def doCleanUp(self, testName):
        # remove the files from doBeforeFiles
        
        inheritedTestCase = self.beforeFilesInheritFrom(testName)
        if inheritedTestCase != '':
            self.doCleanUp(testName)

        # copy each file to the dir tree
        baseDir = '/opt/testcases/' + testName + '/beforeFiles'
        files=j.system.fs.walk(baseDir, recurse=1, return_folders=0)
        for file in files:
            projectedFile = '/opt/qbase3' + file[len(baseDir):]
            j.system.fs.remove(projectedFile, onlyIfExists=True)

        return True


    def runTests(self):
        j.application.shellconfig.interactive = False
        files   = j.system.fs.listDirsInDir('/opt/testcases/')
        failed = []
        files.sort()
        for file in files:
            baseName = j.system.fs.getBaseName(file)
            if baseName[0]  != '_':
                print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Doing test: ' + baseName
                if self.doTest(baseName):
                    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Test ' + baseName + ' Successfull'
                else:
                    failed.append(baseName)
                    print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Test ' + baseName + ' Failed'

        print 'Failed tests:' + str(failed)
#
#    in_object = None
#
#    def setIn(self, in_object):
#        self.in_object = in_object
#
#    # First it is entered to the buffer than executed
#    def printLastEntry(self):
#        return str(self.in_object[-1])
#
#    def printAllInput(self):
#        return '\n'.join([str(input) for input in self.in_object])