from JumpScale import j
j.application.start('jpackages')

jp= j.packages.findNewest(name="jsjail")

import JumpScale.lib.jail

#make sure you installed using
#http://jumpscale-docs.readthedocs.org/en/latest/spaces/Doc_Jumpscale_Core/Docs/Install/LinuxProduction.html

#make sure all security settings are set properly
# j.tools.jail.prepareJSJail()

j.tools.jail.createJSJailSession(user="user1",secret="1234",session="mysession")

j.application.stop()
