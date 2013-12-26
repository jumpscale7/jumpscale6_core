
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")

    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use: disable_filters: True}}}}\n")

    fields = ['id', 'nid', 'name', 'description', 'active', 'sizeondisk', 'free', 'path']

    out.append('||id||node||name||description||active||free||path||')

    for disk in actor.getVDisks():
        line = [""]

        for field in fields:
            # add links
            if field == 'id':
                line.append('[%s|/grid/disk?id=%s]' % (str(disk[field]), str(disk[field])))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(disk[field]), str(disk[field])))
            elif field == 'sizeondisk':
                continue
            elif field == 'free':
                diskfree = disk[field]
                disksize = disk['sizeondisk']
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
