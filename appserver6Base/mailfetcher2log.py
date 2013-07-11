import time

from pprint import pprint
import cProfile
import pstats

from pylabs.InitBase import *
    
q.application.appname = "mailfetcheractions"
q.application.start()

q.qshellconfig.interactive=True
    
q.core.appserver6.loadActorsInProcess()

def process(mailfrom,emailepoch,subject,text,args):
    
    loghandler=args["loghandler"]
    channel,source=subject.split("_",1)
    if channel.find("CLOUDACTION:")<>-1:
        channel=channel.replace("CLOUDACTION:","")
        for line in text.split("\n"):
            line=line.strip()
            if line<>"":
                splitted=line.split(":")
                
                if len(splitted)==6:                
                    jobguid,start,stop,action,rootobjectguid,state=splitted
                    if action.find(".")==0:
                        msg="could not parse log message, action needs to have actor inside , %s %s\n%s" % (action,subject,text)
                        loghandler.raiseError(self,msg)                         
                    else:
                        actor,action=action.split(".",1)
                        loghandler.log(jobguid,emailepoch,channel,source,actor,rootobjectguid,action,state,start,stop)
                elif len(splitted)==10:
                    #jobid,epochstart,epochend,actionname,rootobjectid,state, customername, spacename, resourcename, resourceguid
                    jobguid,start,stop,action,rootobjectguid,state,customername, spacename, resourcename, resourceguid=splitted
                    if str(customername).strip()=="None":
                        customername=""
                    if str(spacename).strip()=="None":
                        spacename=""
                    if str(resourcename).strip()=="None":
                        resourcename=""
                    if str(resourceguid).strip()=="None":
                        resourceguid=""                   
                    if action.find(".")==0:
                        msg="could not parse log message, action needs to have actor inside , %s %s\n%s" % (action,subject,text)
                        loghandler.raiseError(self,msg)                         
                    else:
                        actor,action=action.split(".",1)
                        loghandler.log(jobguid,emailepoch,channel,source,actor,rootobjectguid,action,state,start,stop,customername, spacename, resourcename, resourceguid)                
                else:
                    msg="could not parse log message, %s\n%s" % (subject,text)
                    from pylabs.Shell import ipshellDebug,ipshell
                    print "DEBUG NOW parseerror"
                    ipshell()
                    
                    loghandler.raiseError(msg)     

lhandler=q.apps.acloudops.actionlogger.extensions.loghandler

#q.core.osis.destroy("acloudops") #remove all existing objects & indexes

#lhandler.loadTypes()

#lhandler.readLogs(hoursago=5*24)

#q.application.stop()

while True:
    print "fetch actions"
    robot=q.tools.mailrobot.get("imap.gmail.com",'action@awingu.com','be343483')
    robot.start(process,loghandler=lhandler)    

    ##check all known actions (active in mem)
    #for key in actionlh.activeActions.keys():
        #action=actionlh.activeActions[key]
        #actionlh.processActionObject(action)
        
    time.sleep(15)
    
    
    #every hour want to save the updated stats
    #q.apps.acloudops.actionhandler.models.actiontype.set(ttype)
    #q.apps.acloudops.actionhandler.models.actiontype.list()

q.application.stop()
