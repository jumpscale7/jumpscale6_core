def main(j,args,params,tags,tasklet):
   
    #create codemgmt recipe
    #a codemanagement recipe is used to define where the code from the code repo needs to go to
    
    recipe=j.packages.getCodeManagementRecipe()
    #repo=j.clients.bitbucket.getRepoConnection("incubaid","pyapps-5.1-businessplanner")
    
    #recipe.add(repo, sourcePath, destinationPath, branch='')
    ##recipe.add(repo,"apps/proposalmaker","/tmp/testdirRemove")  #when outside of sandbox use e.g. /qbase3/... (start with / )
    #recipe.add(repo,"apps/proposalmaker","apps/testdirRemove")  #this will copy inside the sandbox
    
    params.result=recipe  #remember for further usage
    
    return params
    
    
def match(j,args,params,tags,tasklet):
    return True
