from OpenWizzy import o


from .QSocketServer import QSocketServer,QSocketServerFactory

o.base.loader.makeAvailable(o, 'core')
o.system.socketserver = QSocketServerFactory()

