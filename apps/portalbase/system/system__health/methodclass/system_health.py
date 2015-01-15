from JumpScale import j

class system_health(j.code.classGetBase()):

    """
    Alerts handler
    
    """

    def __init__(self):
        self.scl = j.core.osis.getClientForNamespace('system', j.core.portal.active.osis)
        self.acl = j.clients.agentcontroller.get()


    def run(self, nid=None, **kwargs):
        if nid:
            nid = int(nid)
        args = {'nid': nid}
        self.acl.executeJumpscript('jumpscale', 'healthcheck_monitoring', role='master', args=args, gid=j.application.whoAmI.gid, wait=False)
        return True

