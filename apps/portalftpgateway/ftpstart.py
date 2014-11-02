from JumpScale import j
j.application.start('ftpgateway')
j.dirs.tmpDir = j.system.fs.joinPaths(j.dirs.tmpDir, 'ftpcache')
import JumpScale.portal
import JumpScale.baselib.http_client
from pyftpdlib import ftpserver


print "* check nginx & appserver started"
if j.system.net.waitConnectionTest("127.0.0.1", 80, 15) == False or j.system.net.waitConnectionTest("127.0.0.1", 9999, 15) == False:
    msg = "could find a running appserver & nginx webserver."
    raise RuntimeError(msg)
print "* appserver & webserver started."

client = j.core.portal.getPortalClient("127.0.0.1", 80, "1234")

contentmanager = client.getActor("system", "contentmanager", instance=0)
usermanager = client.getActor("system", "usermanager", instance=0)
filemgr = client.getActor("system", "filemanager", instance=0)

ROOTPATH = '/opt/data'
STORPATH = "/opt/data"

j.system.fs.createDir(STORPATH)

#from MetadataHandler import *
from FsSwitcher import FsSwitcher
from FilesystemVirtualRoot import FilesystemVirtualRoot


class Authorizer(ftpserver.DummyAuthorizer):

    def validate_authentication(self, username, password):
        """Return True if the supplied username and password match the
        stored credentials."""
        result = self.usermanager.authenticate(username, password)
        # print "user:%s authenticated:%s" % (username,result)
        return result

    def has_user(self, username):
        result = self.usermanager.userexists(username)
        # print "hasuser:%s" % (username)
        return result

    def has_perm(self, username, perm, path=None):
        result = True
        if path == ".":
            result = True
        # print "hasperm:%s result:%s" % (username,result)
        return result

    def get_perms(self, username):
        """Return current user permissions."""
        result = "elr"
        # print "getperm:%s result:%s" % (username,result)
        return result

    def get_home_dir(self, username):
        """Return the user's home directory, which is root of fs (DO NOT GIVE EMPTY, AT LEAST /)"""
        return "/"

    def get_msg_login(self, username):
        """Return the user's login message."""
        return "hallo"

    def get_msg_quit(self, username):
        """Return the user's quitting message."""
        return "bye"


def processErrorConditionObject(eco):
    print eco
    # from pylabs.Shell import ipshellDebug,ipshell
    # print "DEBUG NOW eco for ftp"
    # ipshell()


def main():

    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = Authorizer()
    authorizer.usermanager = usermanager

    # handler = MyHandler
    handler = ftpserver.FTPHandler
    # handler.abstracted_fs = FilesystemVirtualRoot
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = "pyftpdlib %s based ftpd ready." % ftpserver.__ver__
    handler.contentmanager = contentmanager
    handler.client = client
    handler.filemgr = filemgr
    # handler.filestore=FSIdentifier(STORPATH,usermanager)
    handler._fsSwitcher = FsSwitcher

    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    #handler.masquerade_address = '151.25.42.11'
    #handler.passive_ports = range(60000, 65535)

    # Instantiate FTP server class and listen to 0.0.0.0:21
    address = ('0.0.0.0', 21)
    server = ftpserver.FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()

if __name__ == '__main__':
    main()

j.application.stop()
