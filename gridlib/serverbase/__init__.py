from OpenWizzy import o


from .ServerBaseFactory import ServerBaseFactory

o.base.loader.makeAvailable(o, 'servers')
o.servers.base = ServerBaseFactory()

