from JumpScale import j


class system_docgenerator(j.code.classGetBase()):

    def __init__(self):
        self._te = {}
        self.actorname = "docgenerator"
        self.appname = "system"
        self.host = j.core.portal.runningPortal.dns

    def getDocForActor(self, actorname, **args):
        actorjson = {'swaggerVersion': '1.1', 'basePath': '/',
                     'resourcePath': '/%s' % actorname, 'apis': []}
        routes = j.core.portal.runningPortal.webserver.routes
        for path, route in routes.iteritems():
            (app, actor, method) = path.split('_')
            if actor == actorname.split('__')[1]:
                methodjson = {'path': '/restmachine/%s/%s/%s' % (app, actor, method), 'description': route[4], 'operations': []}
                operationjson = {'httpMethod': 'GET', 'summary': route[4], 'notes': route[4], 'nickname': method.replace('.', '_')}
                if route[2]:
                    operationjson['parameters'] = list()
                    for paramname, paramdoc in route[2].iteritems():
                        paramjson = {'name': paramname, 'description': paramdoc, 'paramType': 'query',
                                     'required': paramdoc.find('optional') == -1, 'allowMultiple': False, 'dataType': 'string'}
                        operationjson['parameters'].append(paramjson)
                methodjson['operations'].append(operationjson)
                actorjson['apis'].append(methodjson)
        return actorjson

    def prepareCatalog(self, **args):
        catalog = {'swaggerVersion': '1.1', 'basePath': '/restmachine/system/docgenerator/getDocForActor?format=jsonraw&actorname='}
        catalog['apis'] = list()
        if 'actors' in args and args['actors']:
            actors = args['actors'].split(',')
        else:
            actors = j.core.portal.runningPortal.webserver.getActors()

        for actor in sorted(actors):
            catalog['apis'].append({'path': '%s' % actor})
        return catalog
