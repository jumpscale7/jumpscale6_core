from JumpScale import j
from system_logs_osis import system_logs_osis


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
            jobs = client.search("null")
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
        return {'result': jobs}
