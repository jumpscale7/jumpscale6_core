
def main(q, args, params, actor, tags, tasklet):
    params.result=None
            
    path3=q.system.fs.joinPaths(params.path,params.dirname+".wiki")
    if not q.system.fs.exists(path3):
        source=q.system.fs.joinPaths(params.spacepath,".space","template.wiki")
        q.system.fs.copyFile(source,path3)

    params.stop=True

    return params

def match(q, args, params, actor, tags, tasklet):
    return True
