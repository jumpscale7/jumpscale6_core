from JumpScale.portal.macrolib import div_base


def main(j, args, params, *other_args):
    return div_base.macro(o, args, params, self_closing=True)


def match(j, args, params, tags, tasklet):
    return True
