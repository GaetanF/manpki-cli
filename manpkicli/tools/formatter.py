import string

class SuperFormatter(string.Formatter):
    """World's simplest Template engine."""

    def get_field(self, field_name, args, kwargs):
        for arg in args:
            if field_name in arg:
                return arg[field_name], None
        return string.Formatter.get_field(self, field_name, args, kwargs)

    @staticmethod
    def generate_table(header, table):
        items = table
        size_cols = []
        line = '+'
        for head in header:
            size_cols.append(len(head) + 2)
        for element in items:
            for i in range(0, len(header)):
                if len(str(element[header[i]])) + 2 > size_cols[i]:
                    size_cols[i] = len(str(element[header[i]])) + 2
        for col in size_cols:
            line += '-' * col + '+'
        graph_table = line + '\n|'
        for i in range(0, len(header)):
            graph_table += " " + header[i] + (" " * (size_cols[i] - len(header[i]) - 1)) + "|"
        graph_table += "\n" + line + "\n"
        for element in items:
            graph_table += "|"
            for i in range(0, len(header)):
                graph_table += " " + str(element[header[i]]) + (" " * (size_cols[i] - len(str(element[header[i]])) - 1)) + "|"
            graph_table += "\n"
        return graph_table + line + "\n"

    @staticmethod
    def generate_list(header, list):
        max_header_length = 0
        for head in header:
            if len(head) > max_header_length:
                max_header_length = len(head)
        graph_list = ''
        for head in header:
            if isinstance(list[head], str):
                item = list[head]
            else:
                item = str(list[head])
            graph_list += head + ' '*(max_header_length-len(head)+2) + ': '+item+'\n'
        return graph_list

    def format_field(self, value, spec):
        if spec.startswith('repeat'):
            template = spec.partition(':')[-1]
            if type(value) is dict:
                value = value.items()
            return ''.join([template.format(item=item) for item in value])
        elif spec.startswith('table'):
            return self.generate_table(spec.partition(':')[-1].split('|'), value)
        elif spec.startswith('list'):
            return self.generate_list(spec.partition(':')[-1].split('|'), value)
        elif spec == 'call':
            return value()
        elif spec.startswith('if'):
            return (value and spec.partition(':')[-1]) or ''
        else:
            return super(SuperFormatter, self).format_field(value, spec)
