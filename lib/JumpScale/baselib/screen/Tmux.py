from JumpScale import j
import time
class Tmux:
    
    def __init__(self):
        self.screencmd="byobu"
    
    def createSession(self,sessionname,screens):
        """
        @param name is name of session
        @screens is list with nr of screens required in session and their names (is [$screenname,...])
        """
        j.system.platform.ubuntu.checkInstall("tmux","tmux")
        j.system.platform.ubuntu.checkInstall("byobu","byobu")
        j.system.process.execute("byobu-select-backend  tmux")
        self.killSession(sessionname)
        if len(screens)<1:
            raise RuntimeError("Cannot create screens, need at least 1 screen specified")
        j.system.process.execute("%s new-session -d -s %s -n %s" % (self.screencmd, sessionname, screens[0]))
        # now add the other screens to it
        if len(screens) > 1:
            for screen in screens[1:]:
                j.system.process.execute("tmux new-window -t '%s' -n '%s'" % (sessionname, screen))

    def executeInScreen(self,sessionname,screenname,cmd,wait=0):
        self.createWindow(sessionname, screenname)
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
        pane = self._getPane(sessionname, screenname)
        if wait<>0:
            cmd2="tmux send-keys -t '%s' '%s;echo $?>%s\n'" % (pane,cmd,ppath)
        else:
            cmd2="tmux send-keys -t '%s' '%s\n'" % (pane,cmd)

        j.system.process.execute(cmd2)  
        time.sleep(wait)
        if j.system.fs.exists(ppath):
            resultcode=j.system.fs.fileGetContents(ppath).strip()
            if resultcode=="":
                resultcode=0
            resultcode=int(resultcode)       
            j.system.fs.remove(ppath)
            if resultcode>0:
                raise RuntimeError("Could not execute %s in screen %s:%s, errorcode was %s" % (cmd,sessionname,screenname,resultcode))
        else:
            j.console.echo("Execution of %s  did not return, maybe interactive, in screen %s:%s." % (cmd,sessionname,screenname))
        if j.system.fs.exists(ppath):
            j.system.fs.remove(ppath)
        if j.system.fs.exists(ppathscript):
            j.system.fs.remove(ppathscript)      

    def getSessions(self):
        cmd = 'tmux list-sessions -F "#{session_name}"'
        exitcode, output = j.system.process.execute(cmd, dieOnNonZeroExitCode=False)
        if exitcode != 0:
            output = ""
        return [ (None, name) for name in output.split() ]
        
    def listSessions(self):
        sessions=self.getSessions()
        for pid,name in sessions:
            print "%s %s" % (pid,name)

    def listWindows(self, session, attemps=5):
        result = dict()
        cmd = 'tmux list-windows -F "#{window_index}:#{window_name}" -t "%s"' % session
        exitcode, output = j.system.process.execute(cmd, dieOnNonZeroExitCode=False)
        if exitcode != 0:
            return result
        for line in output.split():
            idx, name = line.split(':', 1)
            result[int(idx)] = name
        return result

    def createWindow(self, session, name):
        if session not in dict(self.getSessions()).values():
            return self.createSession(session, [name])
        windows = self.listWindows(session)
        if name not in windows.values():
            j.system.process.execute("tmux new-window -t '%s' -n '%s'" % (session, name))

    def windowExists(self, session, name):
        if session in dict(self.getSessions()).values():
            if name in self.listWindows(session).values():
                return True
        return False

    def _getPane(self, session, name):
        windows = self.listWindows(session)
        remap = dict([ (win, idx) for idx, win in windows.iteritems() ])
        result = "%s:%s" % (session, remap[name])
        return result

    def killWindow(self, session, name):
        try:
            pane = self._getPane(session, name)
        except KeyError:
            return # window does nt exist
        cmd = "tmux kill-window -t '%s'" % pane
        j.system.process.execute(cmd)

    def killSessions(self):
        cmd="tmux kill-server"
        j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #todo checking
        
    def killSession(self,sessionname):
        cmd="tmux kill-session -t '%s'"  % sessionname
        j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #todo checking

    def attachSession(self,sessionname):
        j.system.process.executeWithoutPipe("tmux attach - %s" % (sessionname))
