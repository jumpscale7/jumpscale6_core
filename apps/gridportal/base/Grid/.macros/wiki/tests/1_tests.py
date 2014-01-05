import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor = j.apps.actorsloader.getActor("system", "testmanager")
    
    out = []

    #this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    #fields = ['organization', 'enable', 'name', 'license', 'author', 'eco', 'nid', 'priority', 'source', 'state', 'gid', 'result', 'version', 'descr', 'output', 'path', 'testrun', 'id', 'categories']

    fields = ["id", "nid", "name", "organization", "testrun", "state", "enable"]

    out.append('||id||node||name||organization||testrun||state||enable||')

    for test in actor.getTests():
        line = [""]

        for field in fields:
            # add links
            if field == 'id':
                line.append('[%s|/grid/test?id=%s]' % (str(test[field]), str(test[field])))
            elif field == 'nid':
                line.append('[%s|/grid/node?id=%s]' % (str(test[field]), str(test[field])))
            elif field in ('testrun'):
                line.append(str(test[field]).replace('_', '-', 2).replace('_', ' ', 1).replace('_',':'))
            else:
                line.append(str(test[field]))

        line.append("")

        #out.append("|[%s|/grid/node?id=%s]|%s|%s|%s|" % (node["id"], node["id"], node["name"], ipaddr, roles))
        out.append("|".join(line))
    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
