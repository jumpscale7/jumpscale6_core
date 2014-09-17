import requests, base64, phpserialize
from settings import authenticationparams, WHMCS_API_ENDPOINT


class whmcstickets():
    def __init__(self):
        pass

    def _call_whmcs_api(self, requestparams):
        actualrequestparams = dict()
        actualrequestparams.update(requestparams)
        actualrequestparams.update(authenticationparams)
        response = requests.post(WHMCS_API_ENDPOINT, data=actualrequestparams)
        return response

    def create_ticket(self, clientid, deptid, subject, message, priority):
        print 'Creating %s' % subject
        create_ticket_request_params = dict(

                    action = 'openticket',
                    responsetype = 'json',
                    clientid = clientid,
                    subject = subject,
                    deptid = deptid,
                    message = message,
                    priority = priority,
                    noemail = True,
                    skipvalidation= True
                    )
        
        response = self._call_whmcs_api(create_ticket_request_params)
        ticketid = response.ticketid
        return ticketid


    def update_ticket(self, ticketid, deptid, subject, priority, status, userid, email, cc, flag):
        print 'Updating %s' % ticketid
        ticket_request_params = dict(

                    action = 'updateclient',
                    responsetype = 'json',
                    ticketid = ticketid,
                    deptid = deptid,
                    subject = subject,
                    priority = priority,
                    status = status,
                    userid = userid,
                    noemail = True,
                    skipvalidation= True

                    )
        
        response = self._call_whmcs_api(ticket_request_params)
        return response.ok

    def close_ticket(self, ticketid):
        print 'Closing %s' % ticketid
        ticket_request_params = dict(

                    action = 'updateclient',
                    responsetype = 'json',
                    ticketid = ticketid,
                    status = 'Closed',
                    noemail = True,
                    skipvalidation= True

                    )
        
        response = self._call_whmcs_api(ticket_request_params)
        return response.ok


    def get_ticket(self, ticketid):
        import xml.etree.cElementTree as et
        print 'Closing %s' % ticketid
        ticket_request_params = dict(

                    action = 'updateclient',
                    responsetype = 'json',
                    ticketid = ticketid,
                    status = 'Closed',
                    noemail = True,
                    skipvalidation= True

                    )
        
        xs = self._call_whmcs_api(ticket_request_params)
        ticket = dict((attr.tag, attr.text) for attr in et.fromstring(xs))
        return ticket




