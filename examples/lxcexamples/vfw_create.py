from JumpScale import j

j.application.start("vfw_create")

import JumpScale.lib.lxc
import JumpScale.lib.shorewall
import JumpScale.lib.nginx
try:
    import ujson as json
except:
    import json


host = "192.168.40.5"
password = "rooter"

shorewallcl = j.system.platform.shorewall.get(host, password)
nginxcl = j.system.platform.nginx.get(host, password)

fw = {'name': 'vfw'}
fw['tcpForwardRules'] = [{'fromPort': 9999, 'toPort': 80, 'toAddr': '192.168.30.37'}]
fw['wsForwardRules'] = [{'url': '/test', 'toUrls': ['http://192.168.30.37/']}]

shorewallcl.configure(json.dumps(fw))
nginxcl.configure(json.dumps(fw))


j.application.stop()