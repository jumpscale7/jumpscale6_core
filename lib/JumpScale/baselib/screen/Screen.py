from JumpScale import j
import time
class Screen:
    
    def __init__(self):
	self.screencmd="byobu"
    
    def createSession(self,sessionname,screens):
        """
        @param name is name of session
        @screens is list with nr of screens required in session and their names (is [$screenname,...])
        """
    	j.system.platform.ubuntu.checkInstall("screen","screen")
    	j.system.platform.ubuntu.checkInstall("byobu","byobu")
        j.system.process.execute("byobu-select-backend  screen")
    	self.killSession(sessionname)
        if len(screens)<1:
            raise RuntimeError("Cannot create screens, need at least 1 screen specified")
        screens.reverse()
        #-dmS means detatch & create 1 screen session 
        cmd="%s -dmS '%s'"%(self.screencmd,sessionname)
        j.system.process.execute(cmd)
        # now add the other screens to it
        for i in range(len(screens)-1):
            cmd="%s -S '%s' -X screen" % (self.screencmd,sessionname)
            j.system.process.execute(cmd)
        screens.reverse()
        teller=0
        for screenname in screens: 
            cmd="%s -S '%s' -p%s -X title %s" % (self.screencmd,sessionname,teller,screenname)
            teller+=1
            j.system.process.execute(cmd)
        
    def executeInScreen(self,sessionname,screenname,cmd,wait=1):
        ppath=j.system.fs.getTmpFilePath()
        ppathscript=j.system.fs.getTmpFilePath()
        script="""
#!/bin/sh
#set -x

check_errs()
{
  # Function. Parameter 1 is the return code
  # Para. 2 is text to display on failure.
  if [ "${1}" -ne "0" ]; then
    echo "ERROR # ${1} : ${2}"
    echo ${1} > %s    
    # as a bonus, make our script exit with the right error code.
    exit ${1}
  fi
}

%s
check_errs $? 
rm -f %s
""" %(ppath,cmd,ppathscript)
	j.system.fs.writeFile(ppathscript,script)
        cmd2="%s -S %s -p %s -X stuff '%s;echo $?>%s\n'" % (self.screencmd,sessionname,screenname,cmd,ppath)
	#cmd="screen -S %s -p %s -X stuff 'echo %s\nsh %s\n'" % (sessionname,screenname,cmd,ppathscript)
        j.system.process.execute(cmd2)	
	time.sleep(wait)
        if j.system.fs.exists(ppath):
            resultcode=j.system.fs.fileGetContents(ppath).strip()
            if resultcode=="":
                resultcode=0
            resultcode=int(resultcode)       
            j.system.fs.removeFile(ppath)
            if resultcode>0:
                raise RuntimeError("Could not execute %s in screen %s:%s, errorcode was %s" % (cmd,sessionname,screenname,resultcode))
        else:
            j.console.echo("Execution of %s  did not return, maybe interactive, in screen %s:%s." % (cmd,sessionname,screenname))
	if j.system.fs.exists(ppath):
	    j.system.fs.removeFile(ppath)
	if j.system.fs.exists(ppathscript):
	    j.system.fs.removeFile(ppathscript)      
	    
    def getSessions(self):
        cmd="%s -ls" % self.screencmd
        resultcode,result=j.system.process.execute(cmd,dieOnNonZeroExitCode=False)#@todo P2 need to be better checked
        state="start"
        result2=[]
        for line in result.split("\n"):
            if line.find("/var/run/screen")<>-1:
                state="end"
            if state=="list":                
		#print "line:%s"%line
                if line.strip()<>"" and line<>None:
                    line=line.split("(")[0].strip()
                    splitted=line.split(".")
		    #print splitted
                    result2.append([splitted[0],".".join(splitted[1:])])
            if line.find("are screens")<>-1 or line.find("a screen")<>-1:
                state="list"
	    
        return result2
        
    def listSessions(self):
        sessions=self.getSessions()
        for pid,name in sessions:
            print "%s %s" % (pid,name)
            
    def killSessions(self):
	#@todo P1 is there no nicer way of cleaning screens
        cmd="screen -wipe" 
        j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #@todo P2 need to be better checked
        sessions=self.getSessions()
        for pid,name in sessions:
            try:
		j.system.process.kill(int(pid))
	    except:
		j.console.echo("could not kill screen with pid %s" % pid)
        cmd="screen -wipe" 
        j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #todo checking
        
    def killSession(self,sessionname):
        cmd="screen -wipe" 
        j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #todo checking
        sessions=self.getSessions()	
        for pid,name in sessions:
            if name.strip().lower()==sessionname.strip().lower():
		try:
		    j.system.process.kill(int(pid))
		except:
		    j.console.echo("could not kill screen with pid %s" % pid)
		cmd="screen -wipe" 
		j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #todo checking

    def attachSession(self,sessionname):
        #j.system.process.executeWithoutPipe("screen -d -r %s" % sessionname)
	j.system.process.executeWithoutPipe("%s -d -r %s" % (self.screencmd,sessionname))