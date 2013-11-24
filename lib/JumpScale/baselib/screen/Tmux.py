from JumpScale import j
import time
import os
class Tmux:
    
    def __init__(self):
        self.screencmd="tmux"
    
    def createSession(self,sessionname,screens):
        """
        @param name is name of session
        @screens is list with nr of screens required in session and their names (is [$screenname,...])
        """
        j.system.platform.ubuntu.checkInstall("tmux","tmux")
        self.killSession(sessionname)
        if len(screens)<1:
            raise RuntimeError("Cannot create screens, need at least 1 screen specified")
        j.system.process.execute("%s new-session -d -s %s -n %s" % (self.screencmd, sessionname, screens[0]))
        # now add the other screens to it
        if len(screens) > 1:
            for screen in screens[1:]:
                j.system.process.execute("tmux new-window -t '%s' -n '%s'" % (sessionname, screen))

    def executeInScreen(self,sessionname,screenname,cmd,wait=0, cwd=None, env=None, newscr=False):
        """
        @param sessionname Name of the tmux session
        @type sessionname str
        @param screenname Name of the window in the session
        @type screenname str
        @param cmd command to execute
        @type cmd str
        @param wait time to wait for output
        @type wait int
        @param cwd workingdir for command only in new screen see newscr
        @type cwd str
        @param env environment variables for cmd onlt in new screen see newscr
        @type env dict
        @param newscr run process in newly created window usefull for checking status
        @type newscr bool
        """
        env = env or dict()
        envstr = ""
        for name, value in env.iteritems():
            envstr += "export %s=%s\n" % (name, value)
        ppath=j.system.fs.getTmpFilePath()
        scriptfile = j.system.fs.getTmpFilePath()
        workdir = ""
        if cwd:
            workdir = "cd %s" % cwd
        script="""
#!/bin/sh
#set -x

%(env)s
%(cwd)s
%(cmd)s
echo "$?" > %(out)s
rm $0
    """ % {'env': envstr, 'cwd': workdir, 'cmd': cmd, 'out': ppath}
        j.system.fs.writeFile(scriptfile, script)
        os.chmod(scriptfile, 0755)
        if newscr:
            self.killWindow(sessionname, screenname)
            if sessionname not in dict(self.getSessions()).values():
                cmd2 = "tmux new-session -d -s '%s'" % sessionname
            else:
                cmd2 = "tmux new-window -t '%s'" % sessionname
            cmd2 += " -n '%s' '%s'" % (screenname, scriptfile)
        else:
            self.createWindow(sessionname, screenname)
            pane = self._getPane(sessionname, screenname)
            cmd2="tmux send-keys -t '%s' '%s\n'" % (pane,cmd)

        j.system.process.execute(cmd2)  
        time.sleep(wait)
        if wait and j.system.fs.exists(ppath):
            resultcode=j.system.fs.fileGetContents(ppath).strip()
            j.system.fs.remove(ppath)
            if not resultcode or int(resultcode)>0:
                raise RuntimeError("Could not execute %s in screen %s:%s, errorcode was %s" % (cmd,sessionname,screenname,resultcode))
        elif wait:
            j.console.echo("Execution of %s  did not return, maybe interactive, in screen %s:%s." % (cmd,sessionname,screenname))
        if j.system.fs.exists(ppath):
            j.system.fs.remove(ppath)

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

    def logWindow(self, session, name, filename):
        pane = self._getPane(session, name)
        cmd = "tmux pipe-pane -t '%s' 'tee -a \"%s\" | jslogpipe -n \"%s\"'" % (pane, filename, '%s_%s' % (session, name))
        j.system.process.execute(cmd)

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
        j.system.process.execute(cmd, dieOnNonZeroExitCode=False)

    def killSessions(self):
        cmd="tmux kill-server"
        j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #todo checking
        
    def killSession(self,sessionname):
        cmd="tmux kill-session -t '%s'"  % sessionname
        j.system.process.execute(cmd,dieOnNonZeroExitCode=False) #todo checking

    def attachSession(self,sessionname):
        j.system.process.executeWithoutPipe("tmux attach - %s" % (sessionname))
