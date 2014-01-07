from cStringIO import StringIO
import os
from JumpScale import j


# `items` parameter needs to define the tree hierarchically. To do this I use a syntax similar to Python function call.
# This has the interesting property that I can `eval` it with a custom scope. The custom scope allows me to define items
# which are not already defined, and return the structure that I need.
class Scope(dict):

    def __init__(self, value=None):
        self.value = value

    def __getattr__(self, attr, *args):
        return self

    def __getitem__(self, item):
        return Scope((item, []))

    def __call__(self, *args):
        args = [Scope._str_to_scope(arg) for arg in args]
        self.value = (self.value[0], args)
        return self

    @staticmethod
    def _str_to_scope(str):
        # If there is a string argument, convert it to type scope
        if isinstance(str, basestring):
            return Scope((str, []))
        else:
            return str

    def __str__(self):
        return repr(self.value)

    __repr__ = __unicode__ = __str__


# The generated parse tree will be a tree of `Scope`s. This function convert it to a tree of strings.
def simplify(expr):
    if isinstance(expr, Scope):
        return simplify(expr.value)
    elif isinstance(expr, (list, tuple)):
        return [simplify(e) for e in expr]
    else:
        return expr


def parse_children_tree(expr):
    return simplify([Scope._str_to_scope(s) for s in eval(expr, Scope())])


def dir_children(dir_name):
    """Return a _sorted_ list of the _full path_ of the children of a directory"""
    # If a directory contains a .order file, then it's used for base of sorting. If it doesn't, then files are ordered alphabetically
    #
    # The format of .order file is like the following
    #
    #   1:Doc 1
    #   2:Doc 3
    #   3:Doc 2
    # 
    # I parse the file & sort it based on the page index, then keep the sorted files in _doc_order_cache
    if not os.path.isdir(dir_name):
        return []

    order_file = os.path.join(dir_name, '.order')
    if not os.path.exists(order_file):
        return sorted(os.path.join(dir_name, f) for f in os.listdir(dir_name))
    else:
        docs = sorted([line.split(':') for line in j.system.fs.fileGetContents(order_file).splitlines()], key=lambda line: int(line[0]))
        return [os.path.join(dir_name, f + '.wiki') for f in zip(*docs)[1]]


def is_wiki_page(child):
    if os.path.basename(child).startswith('.'):
        return False

    parent, child_name = os.path.split(child)
    if child_name.endswith('.wiki') and os.path.basename(parent) == os.path.splitext(child_name)[0]:
        return False

    return os.path.isdir(child) or child.endswith('.wiki')



def get_dir_tree(dir_name, max_depth=1, items=None):
    if max_depth == 0:
        return []

    Infinity = float('inf')

    if items:
        items_order = {item.lower(): order for order, item in enumerate(items)}
        items_key = lambda x: items_order.get(os.path.basename(x[0]).lower(), Infinity)
        items_filter = lambda x: os.path.splitext(os.path.basename(x).lower())[0] in items_order
    else:
        items_filter = lambda x: True

    return [(child, get_dir_tree(child, max_depth=max_depth - 1))
                  for child in dir_children(dir_name)
                  if is_wiki_page(child) and items_filter(child)]


def format_dir_tree(dir_tree, space_name, bullets=False, tree=False, depth=1):
    if not dir_tree:
        return ''

    start_format = '<ul class="{0} {1}">'.format('nav nav-list' if not bullets else '', 'tree' if tree else '')

    s = StringIO()
    s.write(start_format)
    for node, children in dir_tree:
        if os.path.isdir(node):
            wiki_name = os.path.basename(node)
        else:
            wiki_name = os.path.basename(os.path.splitext(node)[0])
        s.write('<li><a href="/{1}/{0}">{0}</a>'.format(wiki_name, space_name))
        s.write(format_dir_tree(children, space_name, bullets, False, depth + 1))
        s.write('</li>')
    s.write('</ul>')
    return s.getvalue()


def main(j, args, params, tags, tasklet):
    doc = args.doc
    page = args.page
    params.result = page
    bullets = args.tags.labelExists('bullets')
    tree = not args.tags.labelExists('no-tree')

    if tree:
        page.addJS(jsLink='/lib/pagetree/pagetree.js')
        page.addCSS('/lib/pagetree/pagetree.css')
        js_content = '$(function(){$(".tree").pagetree()});'
        if js_content not in page.head:
            page.addJS(jsContent=js_content)

    MAX_DEPTH = 3

    if args.tags.tagExists('depth'):
        depth = int(args.tags.tagGet('depth'))
    else:
        depth = MAX_DEPTH

    if depth == 0:
        depth = MAX_DEPTH

    items = None
    if args.tags.tagExists('items'):
        # The tag "items" can contain spaces. Unfortunately the current implementation doesn't take care of spaces, so
        # I must parse items myself
        m = j.codetools.regex.getRegexMatches(r'items\:\[.*\]', args.cmdstr)
        if m and len(m.matches):
            items = m.matches[0].founditem
            items = items.replace('items:', '', 1)
            items = parse_children_tree(items)

    if args.tags.tagExists('page'):
        pagecontent = args.tags.tagGet('page')
    else:
        pagecontent = None

    if pagecontent:
        if doc.preprocessor.docExists(pagecontent):
            doc = doc.preprocessor.docGet(pagecontent)
        else:
            page.addMessage('MACRO CHILDREN ERROR: Could not find page with name %s to start from.' % pagecontent)
            return params

    dir_name = j.system.fs.getDirName(doc.path)
    dir_tree = items+get_dir_tree(dir_name, depth)
    page.addMessage(format_dir_tree(dir_tree, doc.getSpaceName(), bullets, tree))

    return params


def match(j, args, params, tags, tasklet):
    return True
