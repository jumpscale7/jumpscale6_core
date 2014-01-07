import json
import datetime

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","testmanager")

    id = args.tags.getDict().get('id', None) if not args.tags.getDict().get('id', None).startswith('$$') else None

    details =args.tags.labelExists("details")
    script = args.tags.labelExists("scriptsource")

    if id==None:
        params.result = ('Test id needs to be specified, param name:id')
        return params

    obj = actor.getTests(id=id)
    if not obj:
        params.result = ('Test %s not found'%id)
        return params

    obj = obj
    out= "h2. Test %s\n" % id

    if not obj.has_key("nid"):
        obj["nid"]=0

    out += "* gid: %s, nid: %s\n" % (obj["gid"], obj["nid"])
    out += "* organization: %s\n" % obj["organization"]
    for attr in ['name', 'license', 'author', 'version']:
        if obj[attr]:
            out += "* %s: %s\n" % (attr, obj[attr])
    out += "* Test is %s\n" % obj['state']
    if obj["result"]:
        out += "h3. Result\n"
        out += "{{code:\n"
        out += json.dumps(json.loads(obj["result"]), indent=2)
        out += "\n}}\n"

    if obj['state'] == 'ERROR':
        eco=json.loads(obj["result"])
        ecoguid=eco["guid"]

        out +="h3. Error Condition Info\n"
        out +="{{eco: guid:%s}}\n" % ecoguid

    if details:
        out += "h3. Additional Info\n"
        out2 = ['||Property||Value||']
        if obj['testrun']:
            out2.append("|Testrun|%s|" % obj['testrun'].replace('_', '-', 2).replace('_', ' ', 1).replace('_',':'))
        if obj['categories']:
            out2.append('|categories|%s|' % ', '.join(obj['categories']))
        for attr in ['enable', 'priority', 'descr', 'output', 'path']:
            if obj[attr]:
                out2.append('|%s|%s|' % (attr, obj[attr]))
        out += '\n'.join(out2)

    if script:
        out+= "\nh3. Script Source\n"
        scriptsource = ''
        for fname, fcode in obj["source"].iteritems():
            scriptsource += 'def %s:\n%s' % (fname, fcode)
        out += "{{code: \n%s\n}}\n" % scriptsource
            # out += 'h5. %s\n' % fname
            # out += "{{code: %s\n}}\n" % fcode

    params.result = (out, doc)

    return params



def match(j, args, params, tags, tasklet):
    return True
