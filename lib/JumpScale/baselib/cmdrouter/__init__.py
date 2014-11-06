from JumpScale import j

from .CmdRouterFactory import JumpscrCmdRouterFactoryptFactory

j.base.loader.makeAvailable(j, 'core')
j.core.cmdrouter = CmdRouterFactory()
