import requests, base64, phpserialize
from settings import authenticationparams, WHMCS_API_ENDPOINT, OPERATIONS_USER_ID, MOTHERSHIP1_OPERATIONS_DEPARTMENT_ID
import json
import xml.etree.cElementTree as et


class whmcstickets():
    def __init__(self):
        pass

    def _call_whmcs_api(self, requestparams):
        actualrequestparams = dict()
        actualrequestparams.update(requestparams)
        actualrequestparams.update(authenticationparams)
        response = requests.post(WHMCS_API_ENDPOINT, data=actualrequestparams)
        return response

    def list_deps(self):        
        params = dict(action='getsupportdepartments')
        response = self._call_whmcs_api(params)
        result = dict((attr.tag, attr.text) for attr in et.fromstring(response.content))
        return result

    def create_ticket(self, subject, message, priority, clientid=OPERATIONS_USER_ID, deptid=MOTHERSHIP1_OPERATIONS_DEPARTMENT_ID):
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
        ticketid = json.loads(response.content)['tid']
        return ticketid


    def update_ticket(self, ticketid, subject, priority, status, email, cc, flag, userid=OPERATIONS_USER_ID, deptid=MOTHERSHIP1_OPERATIONS_DEPARTMENT_ID):
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




