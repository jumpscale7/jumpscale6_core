
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")

    out = []
    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    fields = ["id", "nid", "active", "ssd", "model", "path", "size", "free", "fs", "mounted", "name", "description", "type", "mountpoint"]

    header = [""]
    for field in fields:
        header.append(field)
    header.append("")
    out.append('||'.join(header))

    # from IPython import embed
    # embed()

    for disk in actor.getDisks():
        line = [""]

        for field in fields:
            line.append(str(disk[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
