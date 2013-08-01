# -*- encoding: utf-8 -*-
import re
from django import template

register = template.Library()

@register.tag(name="stripempty")
def do_stripempty(parser, token):
    nodelist = parser.parse(('endstripempty',))
    parser.delete_first_token()
    return StripEmptyNode(nodelist)

class StripEmptyNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        output = self.nodelist.render(context)
        lines = output.split("\n")
        nonempty_lines = [l for l in lines if not re.match('^\w*$', l)]
        return '\n'.join(nonempty_lines)
