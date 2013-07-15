
def main(o, args, params, actor, tags, tasklet):
    #create 3 types of macro dirs inside
    o.system.fs.createDir(o.system.fs.joinPaths(params.path,"wiki"))
    o.system.fs.createDir(o.system.fs.joinPaths(params.path,"preprocess"))
    o.system.fs.createDir(o.system.fs.joinPaths(params.path,"page"))
    params.stop=True    
    return params

def match(o, args, params, actor, tags, tasklet):
    return params.dirname==".macros"
