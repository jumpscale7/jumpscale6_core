
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}}}\n")
    nid = args.getTag('nid')

    fields = ["path", "nid", "mountpoint", "ssd", "size", "free", "mounted"]

    out.append('||path||node||mountpoint||ssd||usage||mounted||')

    disks = actor.getDisks(nid=nid)

    if not disks:
        params.result = ('No disks found', doc)
        return params

    for disk in disks:
        line = [""]

        for field in fields:
            # add links
            if field == 'path':
                line.append('[%s|/grid/disk?id=%s&nid=%s]' % (str(disk[field]), str(disk['id']), disk['nid']))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(disk[field]), str(disk[field])))
            elif field == 'size':
                disksize = disk[field]
            elif field == 'free':
                diskfree = disk[field]
                if not disksize or not diskfree:
                    diskusage = 'N/A'
                else:
                    diskusage = '%s%%' % (100 - int(100.0 * diskfree / disksize))
                line.append(diskusage)
            else:
                line.append(str(disk[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
