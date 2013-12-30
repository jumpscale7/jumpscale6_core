
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")

    machineid = args.tags.getDict().get("machineid", None)
    disk_id = args.tags.getDict().get("disk_id", None)

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use: disable_filters:True}}}}\n")

    fields = ['id', 'nid', 'name', 'description', 'active', 'sizeondisk', 'free', 'path']

    out.append('||id||node||name||description||active||free||path||')
    vdisks = actor.getVDisks(machineid=machineid, disk_id=disk_id)

    if not vdisks:
        params.result = ('No disks found', doc)
        return params

    for vdisk in vdisks:
        line = [""]

        for field in fields:
            # add links
            if field == 'id':
                line.append('[%s|/grid/vdisk?id=%s]' % (str(vdisk[field]), str(vdisk[field])))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(vdisk[field]), str(vdisk[field])))
            elif field == 'sizeondisk':
                continue
            elif field == 'free':
                diskfree = vdisk[field]
                disksize = vdisk['sizeondisk']
                diskusage = 100 - int(100.0 * diskfree / disksize)
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
