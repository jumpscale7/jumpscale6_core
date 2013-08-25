
def main(o, args, params, tags, tasklet):
    params.merge(args)

    params.result = ""

    if "error" in params.paramsExtra:
        # params.doc.content.replace(params.macrostr,)
        params.result = paramsExtra["error"]

    params.result = (params.result, params.doc)

    return params


def match(o, args, params, tags, tasklet):
    return True
