from OpenWizzy import o
from HttpClient import HttpClient 

class Empty():
    pass

if not  o.__dict__.has_key("clients"):
    o.clients=Empty()

o.clients.http=HttpClient()


