import datetime
import json

def main(j, args, params, tags, tasklet):

    params.merge(args)
    doc = params.doc
    # tags = params.tags

    passwd = j.application.config.get("grid.master.superadminpasswd")
    osis = j.core.osis.getClient(j.application.config.get("grid.master.ip"), passwd=passwd, user='root')
    osis_test = j.core.osis.getClientForCategory(osis,"system","test")

    tid = args.getTag('id')
    if not tid:
        out = 'Test id needs to be specified, param name:id'
        params.result = out, doc
        return params

    tests = osis_test.simpleSearch({'id': tid})
    if not tests:
        out = 'Could not find test with id %s' % tid
        params.result = out, doc
        return params

    obj = tests[0]

    out = """{{jscript

$( function () {
    $(".testruncontainer").hide();
    $('h3').click(function() { $(this).next(".testruncontainer").toggle("fast") });
});
}}
"""
    out += "h2. TestRun %(state)s\n"%  obj

    out +="* gid:%s nid:%s\n"%(obj["gid"],obj["nid"])
    out +="* Categories: %s\n"%(', '.join(obj["categories"]))
    if  obj["descr"]:
        out +="* Description : %s\n"%obj["descr"]
    out +="* Priority: %(priority)s\n"%obj
    out +="* Verion: %(version)s\n"%obj

    if obj['state'] != 'INIT':
        out += "* start:%s\n"% (datetime.datetime.fromtimestamp(obj["starttime"]).strftime('%Y-%m-%d %H:%M:%S'))

    if obj["state"]=="ERROR":
        out +="* Test has FAILED.\n"

    elif obj['state']  == 'OK':
        out +="* Test completed at "
        out += "%s\n"% datetime.datetime.fromtimestamp(obj["endtime"]).strftime('%Y-%m-%d %H:%M:%S')

    if obj['output']:
        for testname, output in obj['output'].iteritems():
            teststate = obj['teststates'].get(testname, 'UNKNOWN')
            out += "h3. [Test: %s %s|#]\n" % (testname, teststate)
            out += "{{div: class=testruncontainer}}\n"
            out += "h4. Source\n"
            out += "{{code\n%s\n}}\n" % obj['source'].get(testname, '')
            if teststate == 'OK':
                out += "h4. Result\n"
                out += "{{code\n%s\n}}\n" % obj['result'].get(testname, '')
            elif testname in obj['result']:
                out += "h4. ECO\n"
                out += "{{grid.eco id:%s}}\n" % obj['result'][testname]

            out += "h4. Output\n"
            out += "{{code\n%s\n}}\n" % output
            out += "{{div}}\n"

    params.result = (out, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
