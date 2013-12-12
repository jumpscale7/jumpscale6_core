
from JumpScale import j

j.application.start("dataimport")


import JumpScale.portal



pc=j.core.portal.getPortalClient("127.0.0.1",port=8005,secret="1234")
tm=pc.getActor("test","taskmanager")
tm.model_user_create("incubaid","despiegk","kristof@adomain.com,kristof2@me.com",groups="group1,group2")

from IPython import embed
print "DEBUG NOW ooo"
embed()
