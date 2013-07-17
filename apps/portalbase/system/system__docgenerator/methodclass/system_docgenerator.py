from OpenWizzy import o
from system_docgenerator_osis import system_docgenerator_osis

class system_docgenerator(system_docgenerator_osis):

    def __init__(self):
        self._te={}
        self.actorname="docgenerator"
        self.appname="system"
        self.host = o.core.portal.runningPortal.dns
        system_docgenerator_osis.__init__(self)

    def getDocForActor(self, actorname, **args):
        actorjson = {'swaggerVersion': '1.1', 'basePath': 'http://%s'%self.host,
                     'resourcePath': '/%s'%actorname, 'apis': []}
        routes = o.core.portal.runningPortal.webserver.routes
        for path, route in routes.iteritems():
            (app, actor, method) = path.split('_')
            if actor == actorname.split('__')[1]:
                methodjson = {'path': '/restmachine/%s/%s/%s' % (app, actor, method),'description': route[4], 'operations': []}
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
        catalog = {'swaggerVersion': '1.1', 'basePath': 'http://%s/restmachine/system/docgenerator/getDocForActor?format=jsonraw&actorname='%self.host}
        catalog['apis'] = list()
        if args.has_key('actors') and args['actors']:
            actors = args['actors'].split(',')
        else:
            actors = o.core.portal.runningPortal.webserver.getActors()

        for actor in sorted(actors):
            catalog['apis'].append({'path': '%s'%actor})
        return catalog
