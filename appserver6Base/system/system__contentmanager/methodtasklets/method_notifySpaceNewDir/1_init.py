
def main(q, args, params, actor, tags, tasklet):
    
    params.merge(args)

    params.path=params.path.replace("\\","/")

    if params.spacepath==None:
        space=q.core.appserver6.runningAppserver.webserver.spacesloader.getSpaceFromId(params.spacename.lower())
        params.spacepath= space.model.path

    params.spacepath=params.spacepath.replace("\\","/")

    params.dirname=q.system.fs.getDirName( params.path+"/", lastOnly=True)
    return params

def match(q, args, params, actor, tags, tasklet):    
    return True
