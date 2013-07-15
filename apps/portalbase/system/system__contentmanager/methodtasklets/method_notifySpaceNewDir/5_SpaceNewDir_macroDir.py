
def main(o, args, params, actor, tags, tasklet):
    #create 3 types of macro dirs inside
    source=None
    if params.path.find(".macros/page")<>-1:
        source=o.system.fs.joinPaths(o.system.fs.getDirName(tasklet.path),".templates",".macros","defaultpagemacro.py")
    elif params.path.find(".macros/preprocess")<>-1:
        source=o.system.fs.joinPaths(o.system.fs.getDirName(tasklet.path),".templates",".macros","defaultpreprocessmacro.py")
    elif params.path.find(".macros/wiki")<>-1:
        source=o.system.fs.joinPaths(o.system.fs.getDirName(tasklet.path),".templates",".macros","defaultwikimacro.py")

    dest=o.system.fs.joinPaths(params.path,"5_%s.py"%params.dirname)
    if source<>None:
         o.system.fs.copyFile(source,dest)

    params.stop=True    
    return params

def match(o, args, params, actor, tags, tasklet):
    return params.path.find(".macros")<>-1
