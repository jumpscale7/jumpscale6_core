def main(j,args,params,tags,tasklet):
   
    #package code from codemgmt recipe

    jp=args.jp

    recipe=jp.actions.code_getRecipe()

    # platform=args.platform
    # platform="generic"
    platform=j.console.askChoice(j.system.platformtype.getPlatforms(),descr="choose which platform you want to package for")

    recipe.package(qp, platform)
    #this is the standard used package function, can overrule to do custom work
    
    return params
    
    
def match(j,args,params,tags,tasklet):
    
    return True
