import datetime

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing vdisk id param "id"'
        params.result = (out, args.doc)
        return params

    vdisks = j.apps.system.gridmanager.getMachines(id=id)
    if not vdisks:
        params.result = ('VDisk with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = vdisks[0]
        for attr in ['lastcheck', 'expiration', 'backuptime']:
            obj[attr] = datetime.datetime.fromtimestamp(obj[attr]).strftime('%Y-%m-%d %H:%M:%S')

        netaddr = obj['netaddr']
        netinfo = ''
        for k, v in netaddr.iteritems():
            netinfo += 'mac address: %s, interface: %s, ip: %s<br>' % (k, v[0], v[1])
        obj['netaddr'] = netinfo
        
        for attr in ('roles', 'ipaddr'):
            obj[attr] = ', '.join([str(x) for x in obj[attr]])
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
