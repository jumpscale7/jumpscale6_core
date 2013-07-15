import ast

def main(o,args,params,tags,tasklet):
    page=args.page
    title, rows, headers, width, height, showcolumns, columnAliases, onclickfunction= args.cmdstr.split('|')

    page.addBarChart(title, ast.literal_eval(rows.strip()), list(ast.literal_eval(headers.strip())), width, height, list(ast.literal_eval(showcolumns.strip())), ast.literal_eval(columnAliases.strip()))
    params.result = page 
    return params


def match(o,args,params,tags,tasklet):
    return True

