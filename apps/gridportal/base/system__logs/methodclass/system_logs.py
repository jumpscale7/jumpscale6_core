from JumpScale import j
from system_logs_osis import system_logs_osis
import JumpScale.baselib.serializers


class system_logs(system_logs_osis):

    def __init__(self):
        self._te = {}
        self.actorname = "logs"
        self.appname = "system"
        system_logs_osis.__init__(self)

    def listJobs(self, **args):
        import JumpScale.grid.osis
        osiscl = j.core.osis.getClient()
        client = j.core.osis.getClientForCategory(osiscl, 'system', 'job')

        params = {'ffrom': '', 'to': '', 'nid': '', 'gid': '',
                  'parent': '', 'state': '', 'jsorganization': '', 'jsname': ''}
        for p in params:
            params[p] = args.get(p)

        if not any(params.values()):
            jobs = client.search({})
        else:
            query = {'query': {'bool': {'must': list()}}}
            if params['ffrom']:
                ffrom = params.pop('ffrom')
                starting = j.base.time.getEpochAgo(ffrom)
                drange = {'range': {'timeStart': {'gte': starting}}}
                query['query']['bool']['must'].append(drange)
            if params['to']:
                to = params.pop('to')
                ending = j.base.time.getEpochAgo(to)
                if query['query']['bool']['must']:
                    query['query']['bool']['must'][0]['range']['timeStart']['lte'] = ending
                else:
                    drange = {'range': {'timeStart': {'lte': ending}}}
                    query['query']['bool']['must'].append(drange)
            for k, v in params.iteritems():
                if v:
                    term = {'term': {k: v}}
                    query['query']['bool']['must'].append(term)

            jobs = client.search(query)

        aaData = list()
        fields = ('jsname', 'jsorganization', 'parent', 'roles', 'state')
        for item in jobs['result']:
            itemdata = list()
            for field in fields:
                itemdata.append(item['_source'].get(field))
            itemdata.append('<a href=%s>%s</a>' % ('/gridlogs/job?jobid=%s' % item['_id'], item['_source'].get('args', {}).get('msg', '')))
            result = j.db.serializers.ujson.loads(item['_source'].get('result', ''))
            itemdata.append(result.get('result', ''))
            aaData.append(itemdata)
        return {'aaData': aaData}
