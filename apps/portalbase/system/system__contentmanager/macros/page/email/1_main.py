from OpenWizzy.portal.macrolib import div_base


def main(q, args, params, *other_args):
    return div_base.macro(q, args, params, self_closing=True, tag='input', 
                          additional_tag_params={'type': 'email', 
                                                 'pattern': r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"})


def match(q, args, params, tags, tasklet):
    return True
