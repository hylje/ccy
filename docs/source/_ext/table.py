from importlib import import_module

# Import required docutils modules
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.tables import ListTable
from docutils import io, nodes, statemachine, utils, frontend
from docutils.utils import SystemMessagePropagation

import sphinx


class table_node(nodes.General, nodes.Element):
    pass


class TableDirective(Directive):
    """
    ExcelTableDirective implements the directive.
    Directive allows to create RST tables from the contents
    of the Excel sheet. The functionality is very similar to
    csv-table (docutils) and xmltable (:mod:`sphinxcontrib.xmltable`).

    Example of the directive:

    .. code-block:: rest

    .. table::
     :datafunction: path.to.my.data.function

    """
    #required_arguments = 0
    #optional_arguments = 0
    has_content = False
    option_spec = {'datafunction': directives.path,
                   'class': directives.class_option}

    def run(self):
        """
        Implements the directive
        """
        # Get content and options
        data_path = self.options.get('datafunction', '')
        header = self.options.get('header', True)
        bits = data_path.split('.')
        name = bits[-1]
        path = '.'.join(bits[:-1])
        try:
            module = import_module(path)
        except ImportError:
            return ['Could not import %s' % path]
        try:
            callable = getattr(module, name)
        except Exception:
            return ['Could not import %s from %s' % (name, path)]

        data = callable()
        table = ['<table>']
        if header:
            headers, data = data[0], data[1:]
            table.append('<thead>')
            tr = ['<tr>']
            for head in headers:
                tr.append('<th>%s</th>' % head)
            tr.append('</tr>')
            table.append(''.join(tr))
            table.append('</thead>')
        table.append('</tbody>')
        for row in data:
            tr = ['<tr>']
            for c in row:
                tr.append('<td>%s</td>' % c)
            tr.append('</tr>')
            table.append(''.join(tr))
        table.append('</tbody>')
        table.append('</table>')
        table = '\n'.join(table)
        return [table_node('')]


def setup(app):
    app.add_directive('table', TableDirective)
    app.add_node(table_node)
