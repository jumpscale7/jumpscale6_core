from JumpScale import j


class ProcessCmds():

    def __init__(self,daemon):
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self._name="process"

