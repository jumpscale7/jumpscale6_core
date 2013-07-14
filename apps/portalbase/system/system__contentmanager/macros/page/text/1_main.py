from OpenWizzy.portal.macrolib import div_base


def main(q, args, params, *other_args):
    return div_base.macro(q, args, params, self_closing=True, tag='input', 
                          additional_tag_params={'type': 'text'})


def match(q, args, params, tags, tasklet):
    return True
