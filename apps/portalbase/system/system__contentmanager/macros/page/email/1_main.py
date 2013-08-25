from JumpScale.portal.macrolib import div_base


def main(o, args, params, *other_args):
    return div_base.macro(o, args, params, self_closing=True, tag='input',
                          additional_tag_params={'type': 'email',
                                                 'pattern': r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"})


def match(o, args, params, tags, tasklet):
    return True
