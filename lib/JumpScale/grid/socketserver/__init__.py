from JumpScale import j


from .QSocketServer import QSocketServer, QSocketServerFactory

j.base.loader.makeAvailable(j, 'core')
j.system.socketserver = QSocketServerFactory()
