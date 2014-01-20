import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.getTag("id")
    if not id:
        out = 'Missing alert id param "id"'
        params.result = (out, doc)
        return params

    obj = actor.getAlerts(id=id)[0]

    out = ['||Property||Value||']

    fields = ['id', 'category', 'state', 'description', 'descriptionpub', 'level', 'inittime', 'tags', 'closetime', 'gid', 'lasttime', 'nrerrorconditions', 'errorconditions']

    for field in fields:
        if field in ('errorconditions'):
            out.append("|%s|%s|" % (field.capitalize(), ', '.join(obj[field])))
        elif field == ('lasttime', 'inittime', 'closetime'):
            time = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|%s|%s|" % (field.capitalize(), time))
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))


    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
