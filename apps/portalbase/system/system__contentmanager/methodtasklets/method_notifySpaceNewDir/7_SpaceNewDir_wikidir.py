
def main(o, args, params, actor, tags, tasklet):
    params.result=None
            
    path3=o.system.fs.joinPaths(params.path,params.dirname+".wiki")
    if not o.system.fs.exists(path3):
        source=o.system.fs.joinPaths(params.spacepath,".space","template.wiki")
        o.system.fs.copyFile(source,path3)

    params.stop=True

    return params

def match(o, args, params, actor, tags, tasklet):
    return True
