import datetime
import json

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.tags.getDict().get('id', None) if not args.tags.getDict().get('id', None).startswith('$$') else None

    details =args.tags.labelExists("details")
    logs = args.tags.labelExists("logs")
    children = args.tags.labelExists("children")
    script = args.tags.labelExists("scriptsource")

    if id==None:
        params.result = ('Job id needs to be specified, param name:id')
        return params

    obj = actor.getJobs(id=id)
    if not obj:
        params.result = ("Job '%s' was not found" % id, doc)
        return params

    obj = obj[0]

    out= "h2. Job %s\n"%id

    if not obj.has_key("nid"):
        obj["nid"]=0

    out +="* gid:%s nid:%s  roles:%s \n"%(obj["gid"],obj["nid"],obj["roles"])
    out +="* jumpscript [%s:%s|/grid/jumpscript?jsorganization=%s&jsname=%s]\n"%(obj["jsorganization"],obj["jsname"],obj["jsorganization"],obj["jsname"])
    if  obj["description"]<>"":
        out +="* description : %s\n"%obj["description"]
    out += "* start:%s  (timeout:%s)\n"% (datetime.datetime.fromtimestamp(obj["timeStart"]).strftime('%Y-%m-%d %H:%M:%S'),obj["timeout"])
    if  obj["lock"]<>"":
        out+="lock: %s (duration:%s)\n"%(obj["lock"],obj["lockduration"])


    if obj["state"]=="RUNNING":
        out +="* Job is RUNNING\n"
    if obj["state"]=="ERROR":
        out +="* Job has FAILED.\n"

        eco=json.loads(obj["result"])
        ecoguid=eco["guid"]

        out +="h3. Error Condition Info\n"
        out +="{{eco: guid:%s}}\n"%ecoguid


    else:
        out +="* Job completed at "
        out += "%s\n"% datetime.datetime.fromtimestamp(obj["timeStop"]).strftime('%Y-%m-%d %H:%M:%S')

    if obj["args"]:
        out+="||name||value||\n"
        objargs=json.loads(obj["args"])
        
        for key,value in objargs.iteritems():
            out+="|%s|%s|\n"%(str(key),str(value))

    if logs:
        if obj["result"]:
            out +="h2. Result\n"
            out+="{{code:\n"
            #pretty print the json structure
            out+=json.dumps(json.loads(obj["result"]), indent=2)
            out+="\n}}\n"

        out+= "h3. Logs\n"
        out+= "{{Grid.logs: jid:%s astext}}\n" % id

    if script:
        out+= "h3. Jumpscript\n"
        out+= "{{jumpscript: jsorganization:%s jsname:%s codeonly}}\n"%(obj["jsorganization"],obj["jsname"])

    if children and len(obj["children"])>0:
        out +="h3. Children\n"
        from IPython import embed
        print "DEBUG NOW children macro job, implement"
        embed()
        

    if details:
        out +="h3. Additional Info\n"

        out2 = ['||Property||Value||']

        fields = ['lockduration', 'category', 'source','childrenActive' , 'parent', 'sessionid', 'resultcode']

        for field in fields:
            if field in ('children'):
                out2.append("|%s|%s|" % (field.capitalize(), ', '.join(obj[field])))
            elif field == 'timeStart':
                timeStart = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
                out2.append("|%s|%s|" % (field.capitalize(), timeStart))
            else:
                out2.append("|%s|%s|" % (field.capitalize(), obj[field]))
        out += '\n'.join(out2)

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
