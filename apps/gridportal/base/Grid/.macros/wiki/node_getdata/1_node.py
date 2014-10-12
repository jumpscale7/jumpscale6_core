
try:
    import ujson as json
except:
    import json
def main(j, args, params, tags, tasklet):

    #macro puts obj info as params on doc, when show used as label, shows the content of the obj in nicely structured code block
    nid = args.getTag('id')
    gid = args.getTag('gid')
    if not nid or not gid:
        params.result = ('Node "id" and "gid" must be passed.', args.doc)
        return params
    gid = int(gid)
    osis = j.core.portal.active.osis
    node = osis.get('system', 'node', '%s_%s' % (gid, nid))
    grid = {'name': 'N/A'}
    if osis.exists('system', 'grid', gid):
        grid = osis.get('system', 'grid', gid)
    if not node:
        params.result = ('Node with and id %s_%s not found' % (gid, nid), args.doc)
        return params

    def objFetchManipulate(id):
        #obj is a dict
        node["ipaddr"]=", ".join(node["ipaddr"])
        node["roles"]=", ".join(node["roles"])

        r=""
        for mac in node["netaddr"].keys():
            dev,ip=node["netaddr"][mac]
            r+="|%-15s | %-20s | %s| \n"%(dev,mac,ip)

        node["netaddr"]=r
        node['gridname'] = grid['name']
        return node

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)


def match(j, args, params, tags, tasklet):
    return True


