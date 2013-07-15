from OpenWizzy import o
from .IniFile import InifileTool
o.base.loader.makeAvailable(o, 'tools')
o.tools.inifile = InifileTool()
