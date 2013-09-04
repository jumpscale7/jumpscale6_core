
from JumpScale import j

j.application.start("usercreation")

j.core.appserver6.loadActorsInProcess()
# client=q.core.appserver6.getAppserverClient("127.0.0.1",9999,"1234")
# usermanager=client.getActor("system","usermanager",instance=0)
usermanager = j.apps.system.usermanager

usermanager.usercreate("despiegk", "1234", "", "all,admin", "kristof@despiegeleer.com,kristof@incubaid.com", 0)
usermanager.usercreate("desmedt", "1234", "", "all,admin", "kristof@despiegeleer.com,kristof@incubaid.com", 0)
usermanager.usercreate("dewolft", "1234", "", "all,admin", "kristof@despiegeleer.com,kristof@incubaid.com", 0)
usermanager.usercreate("guest", "1234", "", "guest", "kristof@incubaid.com", 0)


# usermanager.extensions.usermanager.reset()
print "groups for despiegk"
print usermanager.getusergroups("despiegk")
