import datetime
import JumpScale.grid.osis

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    oscl = j.core.osis.getClient(user='root')
    ecocl = j.core.osis.getClientForCategory(oscl, 'system', 'eco')

    id = args.getTag('id')
    if not id:
        out = 'Missing eco id param "id"'
        params.result = (out, doc)
        return params

    obj = ecocl.get(id)
    out = ['||Property||Value||']

    fields = ['appname', 'category', 'jid', 'code', 'level', 'pid', 'nid', 'funcname', 'epoch', 'errormessagePub', 'funclinenr', 'gid', 'masterjid', 'errormessage', 'backtrace', 'type', 'funcfilename', 'tags']

    for field in fields:
        if field == 'nid':
            out.append("|Node|[%s|/grid/node?id=%s]|" % (obj[field], obj[field]))
        elif field == 'pid':
            out.append("|Process|[%s|/grid/process?id=%s]|" % (obj[field], obj[field]))
        elif field == 'jid':
            out.append("|Job|[%s|/grid/job?id=%s]|" % (obj[field], obj[field]))
        elif field == 'gid':
            out.append("|Grid|[%s|/grid/grid?id=%s]|" % (obj[field], obj[field]))
        elif field == 'epoch':
            epoch = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
            out.append("|%s|%s|" % (field.capitalize(), epoch))
        elif field in ['errormessage', 'backtrace']:
            message = obj[field].replace('\n', '<br>').replace(']', '\]').replace('[', '\[')
            out.append("|%s|%s|" % (field.capitalize(), message))
        else:
            out.append("|%s|%s|" % (field.capitalize(), obj[field]))


    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
