
import json
def main(j, args, params, tags, tasklet):

    #macro puts obj info as params on doc, when show used as label, shows the content of the obj in nicely structured code block
    nid = args.getTag('id')
    node = j.apps.system.gridmanager.getNodes(id=nid)
    if not node:
        params.result = ('Node with id %s not found' % nid, args.doc)
        return params

    def objFetchManipulate(id):
        #retrieve nods from actor method
        obj=node[0] #returns 1 node in array (is how the getNodes method works)
        #obj is a dict

        obj["ipaddr"]=", ".join(obj["ipaddr"])
        obj["roles"]=", ".join(obj["roles"])

        r=""
        for mac in obj["netaddr"].keys():
            dev,ip=obj["netaddr"][mac]
            r+="|%-15s | %-20s | %s| \n"%(dev,mac,ip)

        obj["netaddr"]=r
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)


def match(j, args, params, tags, tasklet):
    return True


