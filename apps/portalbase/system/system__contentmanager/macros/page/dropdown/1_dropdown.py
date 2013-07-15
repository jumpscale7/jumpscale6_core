import re
from itertools import izip_longest

def main(o, args, params, tags, tasklet):
    params.result = page = args.page

    # parse params
    multiple_selection = False
    m = re.search(r'\{\{\s*dropdown\s*:\s*(.*)\n', args.macrostr)
    if m:
        attributes = []
        macro_params = [part.strip().split('=') for part in m.group(1).split('|')]
        for pair in macro_params:
            if pair[0].lower() == 'multiple':
                multiple_selection = True

            if len(pair) == 2:
                attributes.append('{}="{}"'.format(*pair))
            else:
                attributes.append(pair[0])
    else:
        attributes = []
    if multiple_selection:
        page.addJS(jsLink='/lib/multiple_selection/multiple_selection.js')
        page.addCSS('/lib/multiple_selection/multiple_selection.css')

    current_option = 0
    options = []
    lines = re.findall(r'\s*(\*+)\s+(.*)', args.cmdstr)
    for ((current_level, current_text), (next_level, _)) in izip_longest(lines, lines[1:], fillvalue=('', '')):
        if len(current_level) < len(next_level):
            options.append('<optgroup label="{0}">'.format(current_text))
            continue

        options.append('<option value="{0}">{0}</option>'.format(current_text))
        if len(current_level) > len(next_level):
            options.append('</optgroup>')
        
    page.addMessage('<select {}>{}</select>'.format(''.join(attributes), ''.join(options)))

    return params


def match(o, args, params, tags, tasklet):
    return True
