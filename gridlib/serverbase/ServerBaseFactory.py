from OpenWizzy import o

from Daemon import Daemon
import time
import struct

class ServerBaseFactory():

    def getDaemon(self, name="unknown",sslorg="",ssluser="",sslkeyvaluestor=None):
        """

        is the basis for every daemon we create which can be exposed over e.g. zmq or sockets or http


        daemon=o.servers.base.getDaemon()

        class MyCommands():
            def __init__(self,daemon):
                self.daemon=daemon

            #session always needs to be there
		    def pingcmd(self,session=session):
		        return "pong"

		    def echo(self,msg="",session=session):
		        return msg

        daemon.setCMDsInterface(MyCommands,category="optional")  #pass as class not as object !!! chose category if only 1 then can leave ""

        #now you need to pass this to a protocol server, its not usable by itself

        """
        
        zd=Daemon(name=name)
        if ssluser<>"":
            from OpenWizzy.baselib.ssl.SSL import SSL
            zd.ssluser=ssluser
            zd.sslorg=sslorg
            zd.keystor=SSL().getSSLHandler(sslkeyvaluestor)            
        else:
            zd.keystor=None
            zd.ssluser=None
            zd.sslorg=None
        return zd

    def initSSL4Server(self,organization,serveruser,sslkeyvaluestor=None):
        from OpenWizzy.baselib.ssl.SSL import SSL
        ks=SSL().getSSLHandler(sslkeyvaluestor)
        ks.createKeyPair(organization, serveruser)

    def getDaemonClientClass(self):
        """
        example usage, see example for server at self.getDaemon (implement transport still)

        DaemonClientClass=o.servers.base.getDaemonClientClass()

        myClient(DaemonClientClass):
            def __init__(self,ipaddr="127.0.0.1",port=5555,org="myorg",user="root",passwd="1234",ssl=False,roles=[]):
                self.init(org=org,user=user,passwd=passwd,ssl=ssl,roles=roles)

            def _connect(self):
                #everwrite this method in implementation to init your connection to server (the transport layer)
                pass

            def _close(self):
                #close the connection (reset all required)
                pass


            def _sendMsg(self, cmd,data,sendformat="m",returnformat="m"):
                #overwrite this class in implementation to send & retrieve info from the server (implement the transport layer)
                #@return (resultcode,returnformat,result)
                #item 0=cmd, item 1=returnformat (str), item 2=args (dict)
                #resultcode
                #    0=ok
                #    1= not authenticated
                #    2= method not found
                #    2+ any other error
                pass
                #send message, retry if needed, retrieve message

        client=myClient()
        print client.echo("atest")

        """
        from DaemonClient import DaemonClient
        return DaemonClient  

    def _serializeBinSend(self,cmd,data,sendformat,returnformat,sessionid):
        lencmd=len(cmd)
        lendata=len(data)
        lenreturnformat=len(returnformat)
        lensendformat=len(sendformat)
        return sessionid + struct.pack("<IIII",lencmd,lendata,lensendformat,lenreturnformat)+cmd+data+sendformat+returnformat

    def _unserializeBinSend(self,data):
        """
        return cmd,data,sendformat,returnformat,sessionid
        """
        sessionid = data[0:12]
        data = data[12:]
        lencmd,lendata,lensendformat,lenreturnformat=struct.unpack("<IIII",data[0:16])
        data = data[16:]
        return data[0:lencmd],data[lencmd:lencmd+lendata],data[lencmd+lendata:lencmd+lendata+lensendformat],data[lencmd+lendata+lensendformat:],sessionid

    def _serializeBinReturn(self,resultcode,returnformat,result):
        lendata=len(result)
        if resultcode==None:
            resultcode=0
        resultcode=int(resultcode)
        lenreturnformat=len(returnformat)
        return struct.pack("<III",resultcode,lenreturnformat,lendata)+returnformat+result

    def _unserializeBinReturn(self,data):
        """
        return resultcode,returnformat,result
        """
        resultcode,lenreturnformat,lendata=struct.unpack("<III",str(data[0:12]))
        return (resultcode,data[12:lenreturnformat+12],data[lenreturnformat+12:])


