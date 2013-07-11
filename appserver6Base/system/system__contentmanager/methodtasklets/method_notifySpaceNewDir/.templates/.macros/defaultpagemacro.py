
def main(q,args,params,tags,tasklet):
    
    page=args.page
    
    page.addMessage(str(params.requestContext.params))
    page.addMessage("this is a test macro tasklet")
    
    #use the page object to add content to the page
    #play with it you can debug in this tasklet
    # use
    #from pylabs.Shell import ipshellDebug,ipshell
    #print "DEBUG NOW IN TEST TASKLET FOR MACRO"
    #ipshell()
    
    return params


def match(q,args,params,tags,tasklet):
    return True

