import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.tags.getDict()["id"]

    obj = actor.getLogs(id=id)[0]

    out = ['||Property||Value||']

    fields = ['id', 'appname', 'category', 'message', 'jid', 'level', 'parentjid', 'pid', 'nid', 'order', 'masterjid', 'epoch', 'gid', 'private', 'aid', 'tags']
    for field in fields:
        if field == 'nid':
            out.append("|Node|[%s|/grid/node?id=%s]|" % (obj[field], obj[field]))
        elif field == 'pid':
            out.append("|Process|[%s|/grid/process?id=%s]|" % (obj[field], obj[field]))
        elif field == 'jid':
            out.append("|Job|[%s|/grid/job?id=%s]|" % (obj[field], obj[field]))
        elif field == 'epoch':
            epoch = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|Time|%s|" % epoch)
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))


    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
