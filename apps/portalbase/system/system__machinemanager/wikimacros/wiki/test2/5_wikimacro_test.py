    
def main(o, i, params, service, tags, tasklet):
    
    doc=params.doc
    tags=params.tags

    params.result="I am the included macro\n"
        
    #the output of this tasklet (params.result) needs to be wiki content
    #the macro will be replaced with the output in the originating wiki doc
    #play with it you can debug in this tasklet
    # use
    #from OpenWizzy.core.Shell import ipshellDebug,ipshell
    #print "DEBUG NOW IN TEST TASKLET FOR MACRO"
    #ipshell()
    

    
    return params


def match(o, i, params, service, tags, tasklet):
    return True

