
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    doc=params.doc
    space = params.paramsExtra.get('space')
    space = params.tags.tagGet('space', space)

    params.result=""

    out=""
    singlespace = False
    if space != 'system':
        spaces = [space] if space else [params.paramsExtra['space']]
        out+='h2. Access Overview of Space "%s"\n\n' % spaces[0]
        singlespace = True
    else:
        spaces=q.core.appserver6.runningAppserver.webserver.spacesloader.spaces.keys()
        out+="h2. Acess Overview of Spaces\n\n"
    
    if spaces:
        if not singlespace:
            out += "||Space"
        out += "||Name||Right||Emails||Groups||Secret url||\n" 
    for spacename in sorted(spaces):
        try:
            space=q.core.appserver6.runningAppserver.webserver.spacesloader.getSpaceFromId(spacename)
        except:
            params.result="ERROR: Could not find space %s"% spacename
            return params 
        
        memberace={}
        for groupname in space.model.acl.keys():
            group=q.apps.system.usermanager.extensions.usermanager.groupGet(groupname)
            if group<>None:
                for membername in group.members:
                    if not memberace.has_key(membername):
                        memberace[membername]=[]
                    right=space.model.acl[groupname]
                    for rightItem in right:
                        if rightItem not in memberace[membername]:
                            memberace[membername].append(rightItem)
        msorted=memberace.keys()
        msorted.sort()
        for name in msorted:
            right=",".join(memberace[name])
            user=q.apps.system.usermanager.extensions.usermanager.userGet(name)
            secreturl="http://%s/%s?authkey=%s" % (q.core.appserver6.runningAppserver.ipaddr,spacename,user.secret)
            if not singlespace:
                out += "|%s" % spacename
            out+="|%s|%s|%s|%s|[secretlink|%s]|\n" % (name,right,",".join(user.emails),",".join(user.groups),secreturl)

    params.result=(out,doc)

    
    return params


def match(q,args,params,tags,tasklet):
    return True

