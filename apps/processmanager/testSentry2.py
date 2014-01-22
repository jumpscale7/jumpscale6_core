from JumpScale import j


j.application.start("reload")
import sys

extra={}
extra["atest"]=1
extra["atest2"]="ddd"

tags="color:green urgent importance:2"

1/0

try:
    print "1"
    1/0
except Exception,e:
    # eco=j.errorconditionhandler.parsePythonErrorObject(e)
    # j.errorconditionhandler.processErrorConditionObject(eco)
    ttype,msg,tb=sys.exc_info()    
    j.errorconditionhandler.sendMessageToSentry("o.wow.module.2",message="a test",ttype="bug",tags=tags,extra=extra,level="fatal",tb=tb)


j.application.stop()