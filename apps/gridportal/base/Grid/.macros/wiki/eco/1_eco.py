import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.getTag('id')
    if not id:
        out = 'Missing eco id param "id"'
        params.result = (out, doc)
        return params

    obj = actor.getErrorconditions(guid=id)

    out = ['||Property||Value||']

    fields = ['appname', 'category', 'jid', 'code', 'level', 'backtrace', 'pid', 'nid', 'funcname', 'epoch', 'errormessagePub', 'funclinenr', 'gid', 'masterjid', 'errormessage', 'type', 'funcfilename', 'tags']
    for field in fields:
        if field == 'nid':
            out.append("|Node|[%s|/grid/node?id=%s]|" % (obj[field], obj[field]))
        elif field == 'epoch':
            epoch = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|%s|%s|" % (field.capitalize(), epoch))
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))


    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
