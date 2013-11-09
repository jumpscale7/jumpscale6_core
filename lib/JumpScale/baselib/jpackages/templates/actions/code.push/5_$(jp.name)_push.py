def main(j,args,params,tags,tasklet):
   
    #push code to remote repo

    jp=args.jp

    recipe=jp.getCodeMgmtRecipe()
    recipe.push()
    #this is the standard used push function, can overrule to do custom work
       
    return params
    
    
def match(j,args,params,tags,tasklet):
    return True
