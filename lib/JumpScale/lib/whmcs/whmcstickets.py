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
        return response.ok


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




