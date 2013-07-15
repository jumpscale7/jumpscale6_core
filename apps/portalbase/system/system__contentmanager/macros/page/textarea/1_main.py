from OpenWizzy.portal.macrolib import div_base


def main(o, args, params, *other_args):
    return div_base.macro(o, args, params, self_closing=True)


def match(o, args, params, tags, tasklet):
    return True
