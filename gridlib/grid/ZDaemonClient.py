from OpenWizzy import o
import OpenWizzy.baselib.serializers
import zmq
import time
ujson = o.db.serializers.ujson
import struct
import math

class ZDaemonClient():
    def __init__(self,ipaddr="localhost", port=4444,datachannel=False,servername="unknownserver"):
        if servername=="":
            raise RuntimeError("servername cannot be empty")
            o.errorconditionhandler.raiseBug(message="servername cannot be empty",category="grid.init") #@todo URGENT: this does not show stacktrace well
        self.retry = True
        self.port=port
        self.ipaddr=ipaddr
        self.datachannel=datachannel
        self.servername=servername
        self.init()
        self.blocksize=8*1024*1024

    def init(self):
        o.logger.log("check if %s is reachable on %s on port %s" % (self.servername,self.ipaddr,self.port), level=4, category='zdaemon.client.init')
        res=o.system.net.waitConnectionTest(self.ipaddr,self.port,20)
        if res==False:
            msg="Could not find a running server instance with name %s on %s:%s"%(self.servername,self.ipaddr,self.port)
            o.errorconditionhandler.raiseOperationalCritical(msgpub=msg,message="",category="zdaemonclient.init",die=True)
        o.logger.log("%s is reachable on %s on port %s" % (self.servername,self.ipaddr,self.port), level=4, category='zdaemon.client.init')

        self.context = zmq.Context()

        self.cmdchannel = self.context.socket(zmq.REQ)

        # if self.port == 4444 and o.system.platformtype.isLinux():
        #     self.cmdchannel.connect("ipc:///tmp/cmdchannel_clientdaemon")
        #     print "IPC channel opened to client daemon"
        # else:
        self.cmdchannel.connect("tcp://%s:%s" % (self.ipaddr,self.port))
        print "TCP channel opened to %s:%s:%s"%(self.servername,self.ipaddr,self.port)

        self.poll = zmq.Poller()
        self.poll.register(self.cmdchannel, zmq.POLLIN)

        if self.datachannel:
            port = int(self.sendcmd("getfreeport"))
            if port == 0:
                raise RuntimeError("Could not find free port on clientdaemon")

            self.datachannel = self.context.socket(zmq.PAIR)
            self.datachannel.connect("tcp://localhost:%s" % port)

            print "init port for datachannel: %s"%port

    def sendMsgOverCMDChannelFast(self, msg):
        self.cmdchannel.send(msg)
        return self.cmdchannel.recv()

    def sendMsgOverCMDChannel(self, msg):
        if self.retry:
            while True:
                # print "Send (%s)" % msg
                self.cmdchannel.send(msg)
                expect_reply = True
                while expect_reply:
                    socks = dict(self.poll.poll(1000))
                    if socks.get(self.cmdchannel) == zmq.POLLIN:
                        reply = self.cmdchannel.recv()
                        if not reply:
                            break
                        else:
                            return reply
                    else:
                        print "W: No response from clientdaemon, retrying"
                        self.reset()
                        self.cmdchannel.send(msg)
            return reply
        else:
            print "Send once (%s)" % msg
            self.cmdchannel.send(msg)
            socks = dict(self.poll.poll(1000))
            if socks.get(self.cmdchannel) == zmq.POLLIN:
                return self.cmdchannel.recv()
            else:
                o.errorconditionhandler.raiseOperationalCritical(message="", category="",
                                                                 msgpub="could not communicate with cmdclient daemon on port %s"%4444, die=True, tags="")

    def close(self):
        try:
            self.cmdchannel.setsockopt(zmq.LINGER, 0)
            self.cmdchannel.close()
        except:
            print "error in close for cmdchannel"
            pass

        try:
            self.poll.unregister(self.cmdchannel)
        except:
            pass

        try:
            self.datachannel.setsockopt(zmq.LINGER, 0)
            self.datachannel.close()
        except:
            # print "error in close for datachannel"
            pass

        self.context.term()

    def reset(self):
        # Socket is confused. Close and remove it.
        self.close()
        self.init()

    def sendblock(self,nsid,authkey,bytestr,compress=True,checkOnServer=True,path="",position=0):
        nsidb=struct.pack("<I",int(nsid))
        hhash=o.base.byteprocessor.hashTiger160(bytestr)
        usize=len(bytestr)
        if compress:
            bytestr=o.base.byteprocessor.compress(bytestr)
            csize=len(bytestr)
            ttype="1"
        else:
            csize=0
            ttype="0"
        if checkOnServer:
            exists=self.sendcmd("exists",nsid=nsid,key=hhash)
            if exists:                
                print "exists:%s pos:%s"%(path,position)
                exists=1
                return (hhash,usize,csize,exists)
        self.sendbinary("%s%s%s%s%s"%(ttype,nsidb,authkey,hhash,bytestr))
        #first byte = is the type, 0 for non compressed, 1 for compressed
        #next 4 bytes is namespace id
        #next 6 bytes are the authkey (redone per session, now fake)
        return (hhash,usize,csize,exists)

    def sendfile(self,nsid,authkey,path,compress=True,checkOnServer=True):   
        keys=[]     
        usize=o.system.fs.statPath(path).st_size
        if usize>self.blocksize: #about 8 MB
            csize=0
            exists=0
            nrblocks=int(math.ceil(float(usize)/float(self.blocksize)))
            for pos in range(nrblocks):
                f=open(path,"r")
                #open file at certain position
                f.seek(pos*self.blocksize)
                bytestr=f.read(self.blocksize)                
                key1,usize1,csize1,exist1=self.sendblock(nsid,authkey,bytestr,compress=compress,checkOnServer=checkOnServer,path=path,position=pos)
                keys.append(key1)
                exists+=exist1
                csize+=csize1
            return (keys,usize,csize,exists)
        else:
            bytestr=o.system.fs.fileGetContents(path)
            key1,usize,csize,exists=self.sendblock(nsid,authkey,bytestr,compress,checkOnServer=checkOnServer,path=path)
            keys.append(key1)
        return (keys,usize,csize,exists)

    def receivefile(self,nsid,authkey,path,keys,checkOnLocalDisk=False): #@todo checkOnLocalDisk needs to be implemented (P1)
        nsidb=struct.pack("<I",int(nsid))

        for key in keys:
            reqstr="5%s%s%s%s"%(1,nsidb,authkey,key)  #the nr 5 tells server to return data from the server
            bytestr=self.sendMsgOverCMDChannel(reqstr)[:-1]
            bytestr=o.base.byteprocessor.decompress(bytestr)
            o.system.fs.writeFile(path, bytestr, append=True)

    def sendbinary(self,bindata):
        return self.sendMsgOverCMDChannel("0%s"%bindata)

    def _raiseError(self, cmd, result):
        if result["state"] == "nomethod":
            msg="execution error on server:%s on %s:%s.\n Could not find method:%s\n"%(self.servername,self.ipaddr,self.port,cmd)
            o.errorconditionhandler.raiseBug(msgpub="msg",message="",category="rpc.exec")
        else:
            eco=o.errorconditionhandler.getErrorConditionObject(result["result"])
            msg="execution error on server:%s on %s:%s.\nCmd:%s\nErrorGUID=%s"%(self.servername,self.ipaddr,self.port,cmd,eco.guid)
            o.errorconditionhandler.raiseOperationalCritical(msgpub="",message=msg,category="rpc.exec",die=True,tags="ecoguid:%s"%eco.guid)            
            # raise RuntimeError("error in send cmd (error on server):%s, %s"%(cmd, result["result"]))


    def sendcmd(self, cmd, rawreturn=False,**args):
        if rawreturn: #means the server will no return a json encoded result dict but the raw output of the method on the server
            data = "31%s"%o.db.serializers.msgpack.dumps([cmd, args])
            data=self.sendMsgOverCMDChannel(data)
            if data[0:7]=="ERROR:":
                self._raiseError(cmd, o.db.serializers.msgpack.loads(data[7:]))
            else:
                return data
        else:
            data = "41%s"%o.db.serializers.msgpack.dumps([cmd, args])
            result = self.sendMsgOverCMDChannel(data)
            result = o.db.serializers.msgpack.loads(result)
            if result["state"] == "ok":
                return result["result"]
            else:
                self._raiseError(cmd, result)
            
    # def sendcmdData(self, cmd, **args):
    #     data = "4%s"%ujson.dumps([cmd, args])
    #     self.datachannel.send(data)


    def perftest(self):
        start = time.time()
        nr = 10000
        print "start perftest for %s for ping cmd"%nr
        for i in range(nr):
            if not self.sendcmd("ping") == "pong":
                raise RuntimeError("ping did not return pong.")
        stop = time.time()
        nritems = nr/(stop-start)
        print "nr items per sec: %s"%nritems
        print "start perftest for %s for cmd ping"%nr
        for i in range(nr):
            if not self.sendcmd("pingcmd") == "pong":
                raise RuntimeError("ping did not return pong.")
        stop = time.time()
        nritems = nr/(stop-start)
        print "nr items per sec: %s"%nritems

class ZDaemonCmdClient(object):
    def __init__(self,ipaddr="localhost", port=4444,datachannel=False,servername="unknownserver", introspect=True):
        self._client = ZDaemonClient(ipaddr, port, datachannel, servername)
        if introspect:
            self._loadMethods()
        
    def _loadMethods(self):
        methodspecs = self._client.sendcmd('_introspect', False)
        for key, spec in methodspecs.iteritems():
            print "key:%s spec:%s"%(key,spec)
            strmethod = """
class Klass(object):
    def __init__(self, client):
        self._client = client

    def method(%s):
        '''%s'''
        return self._client.sendcmd("%s", False, %s)
"""
            Klass = None
            args = [ "%s=%s" % (x, x) for x in spec['args'][0][1:]]
            params = list()
            if spec['args'][3]:
                for cnt, default in enumerate(spec['args'][3][::-1]):
                    cnt += 1
                    spec['args'][0][-cnt] += "=%r" % default
            params = ', '.join(spec['args'][0])
            strmethod = strmethod % (params, spec['doc'], key, ", ".join(args), )
            exec(strmethod)
            klass = Klass(self._client)
            setattr(self, key, klass.method)

