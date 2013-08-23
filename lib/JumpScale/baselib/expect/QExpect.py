# <License type="Sun Cloud BSD" version="2.2">
#
# Copyright (c) 2005-2009, Sun Microsystems, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. Neither the name Sun Microsystems, Inc. nor the names of other
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY SUN MICROSYSTEMS, INC. "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SUN MICROSYSTEMS, INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# </License>

import os
import subprocess
import errno
import time
import sys
from JumpScale import j

PIPE = subprocess.PIPE

if subprocess.mswindows:
    from win32file import ReadFile, WriteFile
    from win32pipe import PeekNamedPipe
    import msvcrt
else:
    import select
    import fcntl
    

if sys.platform.startswith('linux'):
    try:
        import pxssh
    except ImportError, e:
        #We want this to go to stderr, otherwise applications relying on stdout
        #output (build command generator scripts) are pretty busted.
        #print >> sys.stderr, "Module pxssh not found...Wont be able to ssh on linux!!!"
        print "cannot find pxssh"
        pass
    
if sys.platform.startswith('sun') or sys.platform.startswith('linux'):
    try:
        import pexpect
    except ImportError, e:
        print "did not find pexpect"
        j.system.platformtype.isLinux()
        try:
            j.system.platformtype.ubuntu.install("python-pexpect")
        except:
            pass

class Popen(subprocess.Popen):
    def recv(self, maxsize=None):
        return self._recv('stdout', maxsize)

    def recv_err(self, maxsize=None):
        return self._recv('stderr', maxsize)

    def send_recv(self, input='', maxsize=None):
        return self.send(input), self.recv(maxsize), self.recv_err(maxsize)

    def get_conn_maxsize(self, which, maxsize):
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return getattr(self, which), maxsize

    def _close(self, which):
        getattr(self, which).close()
        setattr(self, which, None)

    if subprocess.mswindows:
        def send(self, input):
            if not self.stdin:
                return None

            try:
                x = msvcrt.get_osfhandle(self.stdin.fileno())
                (errCode, written) = WriteFile(x, input)
            except ValueError:
                return self._close('stdin')
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            try:
                x = msvcrt.get_osfhandle(conn.fileno())
                (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
                if maxsize < nAvail:
                    nAvail = maxsize
                if nAvail > 0:
                    (errCode, read) = ReadFile(x, nAvail, None)
            except ValueError:
                return self._close(which)
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close(which)
                raise

            if self.universal_newlines:
                read = self._translate_newlines(read)
            return read

    else:
        def send(self, input):
            if not self.stdin:
                return None

            if not select.select([], [self.stdin], [], 0)[1]:
                return 0

            try:
                written = os.write(self.stdin.fileno(), input)
            except OSError, why:
                if why[0] == errno.EPIPE: #broken pipe
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            flags = fcntl.fcntl(conn, fcntl.F_GETFL)
            if not conn.closed:
                fcntl.fcntl(conn, fcntl.F_SETFL, flags| os.O_NONBLOCK)

            try:
                if not select.select([conn], [], [], 0)[0]:
                    return ''

                r = conn.read(maxsize)
                if not r:
                    return self._close(which)

                if self.universal_newlines:
                    r = self._translate_newlines(r)
                return r
            finally:
                if not conn.closed:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags)


class QExpectTool:
    @staticmethod
    def new(cmd=None):
	'''Create a new Expect session
	
	@param cmd: Command to execute
	@type cmd: string
	
	@returns: Expect session
	@rtype: openwizzy.cmdline.QExpect.QExpect
	'''	
	return QExpect(cmd=cmd or '')
	

class QExpect:
    _p=None      #popen process
    error=False
    _lastsend=""
    _ignoreStdError=False
    _ignoreLineFilter=[]
    _lastOutput=""  #stdOut from last send
    _lastError=""   #stdError from last send
    _cleanStringEnabled=True #if True every output will be cleaned from ansi codes
    _timeout=False #if true a send&wait statement has timed out
    _waitTokens=[] #list of tokens where we wait on when executing

    def __init__(self,cmd=""):
        PIPE = subprocess.PIPE
        if not cmd:
            if cmd=="" and sys.platform.startswith('win'):
                cmd = 'cmd'
            if cmd=="" and not sys.platform.startswith('win'):
                cmd = 'sh'
                self._pxssh = pxssh.pxssh()
            self._p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            
        elif cmd and cmd != 'ssh' and not sys.platform.startswith('win'):
            self._expect = pexpect.spawn(cmd)
            

    def enableCleanString(self):
        """
        All output will be cleaned from ANSI code and other unwanted garbage
        """
        self._cleanStringEnabled=True

    def disableCleanString(self):
        """
        Disable output cleaning, e.g. stripping ANSI code
        """
        self._cleanStringEnabled=False

    def _add2lastOutput(self,str):
        self._lastOutput=self._lastOutput+str

    def _add2lastError(self,str):
        self._lastError=self._lastError+str

    def setIgnoreStdError(self):
        """
        Disable display of stderr error messages to the standard output
        """
        self._ignoreStdError=True

    def unsetIgnoreStdError(self):
        """
        Enable display error output (stderr)
        """
        self._ignoreStdError=False

    def addIgnoreLineFilter(self,filter):
        """
        Add a filter on output lines. Lines matching the provided filter will not be displayed on stdout or stderr.
        """
        self._ignoreLineFilter.append(filter)

    def addWaitToken(self,token):
        """
        Adds a token that we will wait for when using C{self.wait()}
        """
        self._waitTokens.append(token)

    def resetWaitTokens(self,token):
        """
        Remove all tokens we'd wait for in self.wait()
        """
        self._waitTokens=[]

    def clearReceive(self):
        self._lastOutput=""
        self._lastError=""

    def login(self, ip, login, password, login_timeout=15):
        """Log the user into the given server

        By default the prompt is rather optimistic and should be considered more of 
        an example. It is better to try to match the prompt as exactly as possible to prevent
        any false matches by server strings such as a "Message Of The Day" or something. 

        The closer you can make the original_prompt match your real prompt the better. 
        A timeout causes not necessarily the login to fail.

        In case of a time out we assume that the prompt was so weird that we could not match  
        it. We still try to reset the prompt to something more unique. 
        
        If that still fails then we return False.
        """
        if not j.system.platformtype.isLinux():
            raise RuntimeError('pexpect/pxssh not supported on this platform')

        if not self._pxssh.login(ip, login, password, login_timeout=login_timeout):
            raise ValueError('Could not connect to %s, check either login/password are not correct or host is not reacheable over SSH.'%ip)
        else:
            j.logger.log('SSH %s@%s session login successful' % (login, ip), 6)

    def logout(self):
        """This sends exit. If there are stopped jobs then this sends exit twice.
        """
        self.send('logout')

    def receive(self):
        """
        Receive standard out & standard error and returns them as out,error
        This function also remembers these data for later usage in the 
        classes C{_out} & C{_error}.
        """
        if j.system.platformtype.isWindows():
            out=self.receiveOut()
            err=self.receiveError()
            return out,err
        
        elif j.system.platformtype.isLinux() and not self._expect:
            return self._pxssh.before

        elif j.system.platformtype.isUnix() and self._expect:
            
            if self._expect.match:
                return '%s%s'%(self._expect.after, self._expect.buffer)
            
            else:
                return self._expect.before
        
    def receivePrint(self):
        """
        Receive data from stdout and stderr and displays them
        This function also remembers this information for later usage in the 
        classes C{_out} & C{_error}.
        """
        out,err=self.receive()
        self.pprint()

    def receiveOut(self):
        """
        Receive standard out and return. This information is stored for later usage 
        in the class C{_out}.
        """
        out=self._receive(False)
        if self._cleanStringEnabled:
            out=self._cleanStr(out)
        self._add2lastOutput(out)
        j.logger.log("stdout:%s" % out, 9)
        return out

    def receiveError(self):
        """
        Receive standard error and return. This information is stored for later usage 
        in the class C{_error}.
        """
        err=self._receive(True)
        if self._cleanStringEnabled:
            err=self._cleanStr(err)
        self._add2lastError(err)
        return err

    def pprint(self):
        """
        Print the result of all send & receive operations till now on local C{stdout}. 
        """
        out=self._ignoreLinesBasedOnFilter(self._lastOutput)
        error=self._lastError
        if(error<>""):
            j.console.echo("%s/nerror:%s" % (out,error))
        else:
            j.console.echo(out)

    def _receive(self,checkError=False):
        #stdin=self._stdin
        #stdout=self._stdout
        t=.1
        e=1
        tr=5
        p=self._p
        if tr < 1:
            tr = 1
        x = time.time()+t
        y = []
        r = ''
        pr = p.recv
        #check error
        if checkError:
            pr = p.recv_err
        while time.time() < x or r:
            r = pr()
            if r is None:
                if e:
                    raise Exception("Exception occured")
                else:
                    break
            elif r:
                y.append(r)
            else:
                time.sleep(max((x-time.time())/tr, 0))
        returnval=''.join(y)
        returnval=returnval.replace("\\n","\n")
        returnval=returnval.replace("\\r","\r")
        returnval=self._cleanStr(returnval)
        if returnval<>"" and checkError:
            self.error=True
        return returnval

    def _cleanStr(self,s):
        """
        Remove most ANSI characters (screen emulation).
        Remove double prompts (if used e.g. with remote ssh).
        """
        state="start"
        #s=s.encode('ascii')
        strclean=""
        #s=s.replace(unichr(27)+"]0;","")
        s=self._strRemovePromptSSHAnsi(s)
        for item in s:
            if self._ansiCheckStart(item):
                state="ignore"
                teller=0
            if state<>"ignore":
                strclean=strclean+item
            if state=="ignore" and self._ansiCheckStop(item):
                state="ok"
        strclean=strclean.replace(unichr(27)+unichr(7),"")
        strclean=strclean.replace(unichr(27)+unichr(8),"")
        strclean=strclean.replace(unichr(7),"")
        return strclean

    def _strRemovePromptSSHAnsi(self,s):
        state="start"
        strclean=""
        for t in range(0,len(s)):
            if t+3<len(s):
                find=s[t]+s[t+1]+s[t+2]+s[t+3]
            else:
                find=""
            if find==unichr(27)+"]0;":
                #found prompt
                state="ignore"
            if state<>"ignore":
                strclean=strclean+s[t]
            if state=="ignore" and s[t]==unichr(7):
                state="ok"
        return strclean

    def _ansiCheckStart(self,s):
        pattern=[27]
        found=False
        for item in pattern:
            if ord(s)==item:
                found=True
        return found

    def _ansiCheckStop(self,s):
        pattern="cnRhlL()HABCDfsurMHgKJipm"
        found=False
        for item in pattern:
            if ord(s)==ord(item):
                found=True
        return found

    def send(self, data):
        """
        Send a command to shell.
        After sending a command, one of the receive functions must be called to 
        check for the result on C{stdout} or C{stderr}.
        """
        j.logger.log("Executor send: %s" % data, 9)
        self._lastsend=data
        self._lastOutput=""
        self._lastError=""
        
        if j.system.platformtype.isUnix():
            if self._expect:
                if self._expect.sendline(data):
                    return
            
        if j.system.platformtype.isWindows():
            data=data+"\r\n"

        p=self._p

        if len(data) != 0:
            if j.system.platformtype.isWindows():
                sent = p.send(data)
                if sent is None:
                    raise Exception("ERROR: Data sent is none")
                data = buffer(data, sent)
            elif j.system.platformtype.isLinux():
                self._pxssh.sendline(data)

    def prompt(self, timeout=20):
        """Expect the prompt. 
        
        Return C{True} if the prompt was matched.
        Returns C{False} if there was a time out.
        """
        if j.system.platformtype.isLinux():
            self._pxssh.prompt()
        else:
            raise RuntimeError('pexpect/pxssh module not supported on this platform')

    def _removeFirstLine(self,text):
        lines=text.splitlines()
        linenr=0
        cleanstr=""
        for line in lines:
            linenr=linenr+1
            if(linenr<>1):
                cleanstr=cleanstr+line+"\n"
        return cleanstr

    def do(self,data,timeout=30):
        """
        This function is a combination of the functions C{send}, C{receive} and C{print}.

        The first line is also removed (this is the echo from what has been sent).
        Use this if you quickly want to execute something from the command line.
        """
        self.send(data)
        self.wait(timeout)
        self._lastOutput=self._removeFirstLine(self._lastOutput)
        self.pprint()

    #def waitTillEnd(self):
    #    """
    #    @todo not clear what it does anw why needed
    #    """
    #    self._p.wait()

    def _checkForTokens(self,text):
        if text=="":
            return 0
        text=text.lower()
        tokens=self._waitTokens
        tokennr=0
        for token in tokens:
            #j.logger.log("checktoken %s : %s" % (token,text))
            tokennr=tokennr+1
            token=token.lower()
            if text.find(token)<>-1:
                #token found
                j.logger.log("Found token:%s" % token, 9)
                return tokennr
        return 0

    def _ignoreLinesBasedOnFilter(self,str):
        lines=str.splitlines()
        returnstr=""
        for line in lines:
            foundmatch=False
            for filter in self._ignoreLineFilter:
                #print line
                #print filter
                if line.find(filter)<>-1:
                    j.logger.log("Found ignore line:%s:%s" % (filter,line), 9)
                    foundmatch=True
            if foundmatch==False:
                returnstr=returnstr+line+"\n"
        return returnstr

    def wait(self,timeoutval=30):
        """
        Wait until we detect tokens (see L{addWaitToken})

        @param timeoutval: time in seconds we maximum will wait
        """
        j.logger.log("Waiting for receive with timeout:%s " % (timeoutval), 7)
        timeout=False
        starttime=j.system.getTimeEpoch()
        r="" #full return
        returnpart="" #one time return after receive
        done=False #status param
        tokenfound=0
        self._timeout=False
        while(timeout==False and done==False):
            returnpart,err=self.receive()
            tokenfound=self._checkForTokens(returnpart)
            #j.logger.log("tokenfound:%s"%tokenfound)
            returnpart=self._ignoreLinesBasedOnFilter(returnpart)
            r= r+returnpart
            curtime=j.system.getTimeEpoch()
            j.logger.log("TimeoutCheck on waitreceive: %s %s %s" % (curtime,starttime,timeoutval),8)
            if(curtime-starttime>timeoutval):
                j.logger.log("WARNING: execute %s timed out (timeout was %s)" % (self._lastsend,timeoutval), 6)
                timeout=True
            if tokenfound>0:
                done=True
        out,err=self.receive()
        r=r+out
        if timeout:
            r=""
            self._timeout=True
        return tokenfound,r,timeout
    
    def expect(self, outputToExpect):
        """
        Pexpect expect method wrapper
        usage: Excuting a command that expects user input, this method can be used to 
        expect the question asked then send the answer
        Example:
        qexpect = j.tools.expect.new('passwd')
        if qexpect.expect('Enter new'):
            qexpect.send('newPasswd')
            
            if qexpect.expect('Retype new'):
                qexpect.send('anotherPasswd')
                
                if qexpect.expect('passwords do not match'):
                    j.console.echo(qexpect.receive())
        else:
            j.console.echo(qexpect.receive())
        
        """
        j.logger.log('Expect %s '%outputToExpect, 7)
        
        try:
            self._expect.expect(outputToExpect, 2)
            return True
        except:
            j.logger.log('Failed to expect \"%s\", found \"%s\" instead'%(outputToExpect, self.receive()), 7)
        return False