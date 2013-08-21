from OpenWizzy import o
from .CodeGenerator import CodeGenerator
o.base.loader.makeAvailable(o, 'core')
o.core.codegenerator = CodeGenerator()
