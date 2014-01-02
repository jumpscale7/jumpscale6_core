import datetime
import json

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    id = args.tags.getDict().get('id', None)

    details =args.tags.labelExists("details")
    logs = args.tags.labelExists("logs")
    children = args.tags.labelExists("children")
    script = args.tags.labelExists("scriptsource")

    if id==None:
        params.result = ('Job id needs to be specified, param name:id')
        return params

    obj = actor.getJobs(id=id)
    if not obj:
        params.result = ('Job %s not found'%id)
        return params

    obj = obj[0]

    out= "h2. Job %s\n"%id

    if not obj.has_key("nid"):
        obj["nid"]=0

    out +="* gid:%s nid:%s  roles:%s \n"%(obj["gid"],obj["nid"],obj["roles"])
    out +="* jumpscript [%s:%s|/grid/jumpscript?organization=%s&name=%s]\n"%(obj["jsorganization"],obj["jsname"],obj["jsorganization"],obj["jsname"])
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

        out +="h2. Error Condition Info\n"
        out +="{{eco: guid:%s}}\n"%ecoguid


    else:
        out +="* Job completed at "
        out += "%s\n"% datetime.datetime.fromtimestamp(obj["timeStop"]).strftime('%Y-%m-%d %H:%M:%S')

    if obj["args"]<>{}:
        out+="||name||value||\n"
        args=json.loads(obj["args"])
        
        for key,value in args.iteritems():
            out+="|%s|%s|\n"%(str(key),str(value))

    if logs:

        out +="h2. Result\n"
        out+="{{code:\n"
        #pretty print the json structure
        out+=json.dumps(json.loads(obj["result"]),indent=2)
        out+="\ncode}}\n"

        out+= "h2. logs\n"
        out+= "{{logs: jid:%s astext}}\n"

    if script:
        out+= "h2. jumpscript\n"
        out+= "{{jumpscript: domain:%s name:%s codeonly}}\n"%(obj["jsorganization"],obj["jsname"])

    if children and len(obj["children"])>0:
        out +="h2. Children\n"
        from IPython import embed
        print "DEBUG NOW children macro job, implement"
        embed()
        

    if details:
        out +="h2. Additional Info\n"

        out = ['||Property||Value||']

        fields = [  'lockduration', 'category', 'source','childrenActive' , 'parent', 'sessionid', 'resultcode']

        for field in fields:
            if field in ('children'):
                out.append("|%s|%s|" % (field.capitalize(), ', '.join(obj[field])))
            elif field == 'timeStart':
                timeStart = datetime.datetime.fromtimestamp(obj[field]).strftime('%Y-%m-%d %H:%M:%S')
                out.append("|%s|%s|" % (field.capitalize(), timeStart))
            else:
                out.append("|%s|%s|" % (field.capitalize(), obj[field]))

    params.result = ('\n'.join(out), doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
