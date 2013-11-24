import os
print "CLEAN"
for r,d,f in os.walk("/usr"):
    for path in f:
        match=False
        if path.startswith("jscode") or path.startswith("jpackage") or path.startswith("jspackage") or path.startswith("jsdevelop")\
            or path.startswith("jsreinstall") or path.startswith("jsprocess") or path.startswith("jslog") or path.startswith("jsshell"):
            match=True
        if path in ["js"]:
            match=True      
        if match:
            print "remove:%s" % os.path.join(r,path)
            os.remove(os.path.join(r,path))

