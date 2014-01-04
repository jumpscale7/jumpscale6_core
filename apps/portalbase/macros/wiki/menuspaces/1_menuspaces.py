
def main(j, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc
    tags = params.tags

    params.result = ""

    C = """
{{menudropdown: name:Spaces
System:/system
}}
"""
    C="" #@todo fix

    if j.core.webserver.isAdminFromCTX(params.requestContext):
        params.result = C

    params.result = (params.result, doc)

    return params


def match(j, args, params, tags, tasklet):
    return True
