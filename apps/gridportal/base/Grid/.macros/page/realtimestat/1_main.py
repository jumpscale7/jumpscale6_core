def main(j, args, params, tags, tasklet):

    page = args.page
  
    qsparams = args.requestContext.params
    nodeId = qsparams.pop('nodeId', None)

    if nodeId:
        print nodeId

    url = '/restmachine/system/gridmanager/getNodeSystemStats?nodeId=%s' % nodeId

    page.addHTML('<div id="statisticsChart" data-chart ng-model="statisticsData" ng-url="%s" style="width: 100%;"></div>' % url)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
