
from JumpScale import j

import socket
import time

class GraphiteClient():
    def __init__(self):


        self.CARBON_SERVER = '127.0.0.1'
        self.CARBON_PORT = 2003

        
        # self.sock.connect((self.CARBON_SERVER, self.CARBON_PORT))


    def send(self,msg):
        """
        e.g. foo.bar.baz 20
        """
        out=""
        for line in msg.split("\n"):
            out+='%s %d\n'%(line,int(time.time()))
        self.sock = socket.socket()
        self.sock.connect((self.CARBON_SERVER, self.CARBON_PORT))
        self.sock.sendall(out)
        self.sock.close()

    def close(self):
        self.sock.close()