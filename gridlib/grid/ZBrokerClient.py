from JumpScale import j

from ..zdaemon.ZDaemonClient import ZDaemonClient, ZDaemonCmdClient


class ZBrokerClient(ZDaemonCmdClient):

    def __init__(self, ipaddr="localhost", port=5554):
        ZDaemonCmdClient.__init__(self, ipaddr=ipaddr, port=port)
