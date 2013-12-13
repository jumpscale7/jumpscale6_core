
def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    tags = params.tags

    actor=j.apps.actorsloader.getActor("system","gridmanager")

    #this makes sure bootstrap datatables functionality is used
    out="{{datatables_use}}\n\n"

    out+="||id||name||ip||roles||\n"

    for node in actor.getNodes():
        roles=",".join(node["roles"])
        ipaddr=",".join(node["ipaddr"])
        out+="|[%s|/grid/node?id=%s]|%s|%s|%s|\n"%(node["id"],node["id"],node["name"],ipaddr,roles)

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
