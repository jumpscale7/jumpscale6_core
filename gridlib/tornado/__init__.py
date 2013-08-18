from OpenWizzy import o


from .TornadoServer import TornadoServerFactory

o.base.loader.makeAvailable(o, 'servers')
o.servers.tornado = TornadoServerFactory()

