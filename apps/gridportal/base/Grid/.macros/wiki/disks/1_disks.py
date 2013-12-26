
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use: disable_filters: True}}}}\n")


    #fields = ['otherid', 'description', 'roles', 'mem', 'netaddr', 'ipaddr', 'nid', 'lastcheck', 'state', 'gid', 'active', 'cpucore', 'type', 'id', 'name', 'id', 'size', 'devicename', 'disk_id', 'gid', 'role', 'machineid', 'type', 'fs', 'description', 'backuplocation', 'free', 'sizeondisk', 'nid', 'active', 'path', 'name', 'backuptime', 'lastcheck', 'expiration', 'machine_id', 'backup', 'order']

    fields = ["id", "nid", "name", "active", "ssd", "size", "free", "mounted"]

    out.append('||id||node||name||active||ssd||usage||mounted||')

    for disk in actor.getDisks():
        line = [""]

        for field in fields:
            # add links
            if field == 'id':
                line.append('[%s|/grid/disk?id=%s]' % (str(disk[field]), str(disk[field])))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(disk[field]), str(disk[field])))
            elif field == 'size':
                disksize = disk[field]
            elif field == 'free':
                diskfree = disk[field]
                diskusage = 100 - int(100.0 * diskfree / disksize)
                line.append('%s%%' % diskusage)
            else:
                line.append(str(disk[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
