import ast


def main(j, args, params, tags, tasklet):
    page = args.page
    title, rows, headers, width, height, showcolumns, columnAliases, onclickfunction = args.cmdstr.split('|')

    page.addScriptBodyJS("onclickfunction = function(){%s}" % onclickfunction)
    page.addBarChart(title, ast.literal_eval(rows.strip()),
                     list(ast.literal_eval(headers.strip())), width, height,
                     list(ast.literal_eval(showcolumns.strip())),
                     ast.literal_eval(columnAliases.strip()), "onclickfunction")
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
