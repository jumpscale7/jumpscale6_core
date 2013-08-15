

from OpenWizzy import o
from TemplateEngine import TemplateEngine


class TemplateEngineWrapper(object):
    def new(self):
        return TemplateEngine()