
def main(q, args, params, actor, tags, tasklet):
    #create 3 types of macro dirs inside
    q.system.fs.createDir(q.system.fs.joinPaths(params.path,"wiki"))
    q.system.fs.createDir(q.system.fs.joinPaths(params.path,"preprocess"))
    q.system.fs.createDir(q.system.fs.joinPaths(params.path,"page"))
    params.stop=True    
    return params

def match(q, args, params, actor, tags, tasklet):
    return params.dirname==".macros"
