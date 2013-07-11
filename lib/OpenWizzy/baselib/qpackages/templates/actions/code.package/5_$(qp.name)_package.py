def main(q,args,params,tags,tasklet):
   
    #package code from codemgmt recipe

    qp=args.qp

    recipe=qp.actions.code_getRecipe()

    recipe.package(params.owpackage,params.platform)
    #this is the standard used package function, can overrule to do custom work
    
    return params
    
    
def match(q,args,params,tags,tasklet):
    
    return True
