def main(j, args, params, tags, tasklet):

    page = args.page
  
    nid = args.getTag('nid')
    statistic = args.getTag('statistic')
    
    out = ''
    missing = False
    for k, v in (('nid', nid), ('statistic', statistic)):
        if not v:
            out += 'Missing param "%s".<br>' % k
            missing = True

    if missing:
        page.addMessage(out)
        params.result = page
        return params



    page.addBodyAttribute('ng-app="jumpscale"')

    page.addJS(".files/lib/jquery/jquery-1.10.1.js")

    page.addCSS(".files/lib/jqplot-1.0.8/jquery.jqplot.min.css")

    page.addJS(".files/lib/jqplot-1.0.8/jquery.jqplot.min.js")
    page.addJS(".files/lib/jqplot-1.0.8/plugins/jqplot.cursor.min.js")
    page.addJS(".files/lib/jqplot-1.0.8/plugins/jqplot.canvasTextRenderer.min.js")
    page.addJS(".files/lib/jqplot-1.0.8/plugins/jqplot.canvasAxisTickRenderer.js")

    page.addJS(".files/lib/jqplot-1.0.8/plugins/jqplot.canvasAxisLabelRenderer.min.js")
    page.addJS(".files/lib/jqplot-1.0.8/plugins/jqplot.dateAxisRenderer.js")

    page.addJS(".files/lib/jqplot-1.0.8/plugins/jqplot.enhancedLegendRenderer.min.js")

    page.addJS(".files/lib/angular-1.2.5/angular.js")
    page.addJS(".files/app.js")
    page.addJS(".files/directives.js")

    if nid:
        print nid

    url = '/restmachine/system/gridmanager/getNodeSystemStats?nid=%s' % nid
    import random
    randomid = random.randint(1, 999999999999)
    page.addHTML('<div id="statisticsChart%s" data-chart ng-model="statisticsData" ng-url="%s" ng-stat="%s" style="width: 100%%;"></div>' % (randomid, url, statistic))

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True