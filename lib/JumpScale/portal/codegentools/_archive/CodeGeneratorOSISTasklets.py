from JumpScale import j

from CodeGeneratorBase import CodeGeneratorBase

NOTGENSTR = "##DONOTGENERATE##"

tasklets = {}
tasklets["delete"] = """
def main(j, params, args,actor, tags, tasklet):
    #delete
    actor.models.{modelname}.delete(args["guid"])
    return params,True

def match(j, params, args,actor, tags, tasklet):
    return True
"""

tasklets["get"] = """
def main(j, params, args,actor, tags, tasklet): 
    #get obj
    obj=actor.models.{modelname}.get(args["guid"])
    return params,obj

def match(j, params, args,actor, tags, tasklet):
    return True
"""


tasklets["set"] = """
def main(j, params, args,actor, tags, tasklet):
    #create
    obj=actor.models.{modelname}.new()
    return params,obj

def match(j, params, args,actor, tags, tasklet):
    return True
"""

tasklets["find"] = """
def main(j, params, service, tags, tasklet):
    #find
    res=actor.models.{modelname}.find(args["query"])
    if len(res)>100:
        raise RuntimeError("TOO MANY RESULTS FOR QUERY, MAX 100 for {appname}.{actorname}.{modelname} for query:%s"%args["query"])
    return params,res

def match(j, params, args,actor, tags, tasklet):
    return True
"""
tasklets["list"] = """
def main(j, params, args,actor, tags, tasklet):
    #list
    res=actor.models.{modelname}.list()
    if len(res)>100:
        raise RuntimeError("TOO MANY RESULTS FOR LIST, MAX 100 for {appname}.{actorname}.{modelname}")
    return params,res


def match(j, params, args,actor, tags, tasklet):
    return True
"""

tasklets["datatables"] = """
def main(j, params, args,actor, tags, tasklet):
    #list
    from JumpScale.core.Shell import ipshellDebug,ipshell
    print "DEBUG NOW model datatables"
    ipshell()
    
    appname="{appname}"
    actorname="{actorname}"
    modelname="{modelname}"
    modeldb=j.apps.{appname}.{actorname}.models.{modelname}
    res=modeldb.find(params.query)
    if len(res)>100:
        params.result="TOO MANY RESULTS, MAX 100"
    else:
        params.result=res
    return params

def match(j, params, args,actor, tags, tasklet):
    return True
"""


class CodeGeneratorOSISTasklets(CodeGeneratorBase):

    def __init__(self, spec, typecheck=True, dieInGenCode=True, overwrite=True, codepath=None, args=None):
        overwrite = False  # can never overwrite
        CodeGeneratorBase.__init__(self, spec, typecheck, dieInGenCode)
        self.args = args
        self.spec = spec
        self.key = "%s_%s_%s" % (spec.appname, spec.actorname, spec.name)

        self.codepath = j.system.fs.joinPaths(codepath, "osis", spec.name)
        j.system.fs.createDir(self.codepath)
        self.type = "taskletsosis"
        self.overwrite = overwrite

    def generate(self):
        spec = self.spec

        for method in ["set", "get", "delete", "list", "find", "datatables", 'create']:

            path = j.system.fs.joinPaths(self.codepath, "method_%s" % method)
            j.system.fs.createDir(path)

            path = j.system.fs.joinPaths(self.codepath, "method_%s" % method,
                                         "5_%s_%s.py" % (spec.actorname, method))

            path2 = j.system.fs.joinPaths(self.codepath, "method_%s" % method, "5_main.py")
            if j.system.fs.exists(path2):
                j.system.fs.moveFile(path2, path)

            if j.system.fs.exists(path):
                # content=j.system.fs.fileGetContents(path)
                # if content.find(NOTGENSTR)<>-1:
                    # path=j.system.fs.joinPaths(j.core.portal.active.codepath,spec.appname,spec.actorname,method.name,"_5_main.py")
                path = None

            if path != None and str(path) != "":
                # lets also check there are no files in it yet
                if len(j.system.fs.listFilesInDir(j.system.fs.getDirName(path))) == 0:
                    # tags=j.core.tags.getObject(method.tags)
                    content = tasklets[method]
                    content = content.replace("{appname}", spec.appname)
                    content = content.replace("{actorname}", spec.actorname)
                    content = content.replace("{modelname}", spec.name)
                    j.system.fs.writeFile(path, content)

        return self.getContent()
