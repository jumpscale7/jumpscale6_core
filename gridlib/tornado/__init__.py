from OpenWizzy import o


from .TornadoFactory import TornadoFactory

o.base.loader.makeAvailable(o, 'servers')
o.servers.tornado = TornadoFactory()

