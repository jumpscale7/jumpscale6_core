from pylabs.macros import div_base


def main(q, args, params, *other_args):
    return div_base.macro(q, args, params, self_closing=True)


def match(q, args, params, tags, tasklet):
    return True
