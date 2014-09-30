
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc

    actor = j.apps.actorsloader.getActor("system", "gridmanager")

    machineid = args.getTag('machineid')

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}}}\n")

    fields = ['id', 'nid', 'devicename', 'description', 'active', 'sizeondisk', 'free', 'path']

    out.append('||id||node||devicename||description||active||free||path||')
    vdisks = actor.getVDisks(machineid=int(machineid))

    if not vdisks:
        params.result = ('No disks found', doc)
        return params

    for vdisk in vdisks:
        line = [""]
        
        for field in fields:
            # add links
            if field == 'id':
                line.append('[%(id)s|/grid/vdisk?id=%(id)s&gid=%(gid)s]' % vdisk)
            elif field == 'nid':
                line.append('[%(nid)s|/grid/node?id=%(nid)s&grid=%(gid)s]' % vdisk)
            elif field == 'sizeondisk':
                continue
            elif field == 'free':
                diskfree = vdisk[field]
                disksize = vdisk['sizeondisk']
                if disksize:
                    diskusage = 100 - int(100.0 * diskfree / disksize)
                else:
                    diskusage = 0
                line.append('%s%%' % diskusage)
            else:
                line.append(str(vdisk[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
