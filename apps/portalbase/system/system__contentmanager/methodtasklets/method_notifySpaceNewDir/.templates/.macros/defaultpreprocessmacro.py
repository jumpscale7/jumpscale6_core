
def main(o, args, params, tags, tasklet):

    doc = args.doc

    # a preprocess macro manipulates the doc object
    # a preprocess macro is loaded when the appserver starts or when content is changed (not when a user requests content)

    content = "TEST all the rest is gone"

    params.result = (content, doc)

    return params


def match(o, args, params, tags, tasklet):
    return True
