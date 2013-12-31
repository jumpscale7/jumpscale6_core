
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "gridmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}}}\n")

    #['category', 'description', 'level', 'inittime', 'tags', 'closetime', 'id', 'state', 'gid', 'nrerrorconditions', 'lasttime', 'descriptionpub', 'errorconditions']

    fields = ["id", "category", "errorconditions", "description", "state", "level"]

    out.append('||id||category||errorconditions||description||state||level||')

    for alert in actor.getAlerts():
        line = [""]

        for field in fields:
            # add links
            if field == 'id':
                line.append('[%s|/grid/alert?id=%s]' % (str(alert[field]), str(alert[field])))
            elif field == 'errorconditions':
                line.append(' ,'.join(alert[field]))
            else:
                line.append(str(alert[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
