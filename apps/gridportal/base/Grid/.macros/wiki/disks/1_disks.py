
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    # fields = ["id", "nid", "active", "ssd", "model", "path", "size", "free",
    #           "fs", "mounted", "name", "description", "type", "mountpoint"]
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
