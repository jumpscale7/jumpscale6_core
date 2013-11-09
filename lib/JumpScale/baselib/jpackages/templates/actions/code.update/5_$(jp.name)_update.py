def main(j,args,params,tags,tasklet):
   
    #update info into local repo
    
    jp=args.jp

    recipe=jp.getCodeMgmtRecipe()

    if args.has_key("force"):
        recipe.update(args.force)
    else:
        recipe.update()

    #this is the standard used function, can overrule to do custom work
    
    return params
    
    
def match(j,args,params,tags,tasklet):
    return True
