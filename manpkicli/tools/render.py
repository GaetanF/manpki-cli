from ..tools import SuperFormatter
from ..logger import log


class Renderer:
    _render = None

    @staticmethod
    def render(string, endpoint):
        if Renderer.render_exist(endpoint):
            sf = SuperFormatter()
            therender = Renderer.get_render_for_endpoint(endpoint)
            return sf.format(therender, string)
        else:
            return string

    @staticmethod
    def load_render(render):
        Renderer._render = render

    @staticmethod
    def get_render_for_endpoint(endpoint):
        if Renderer.render_exist(endpoint):
            return Renderer._render["render_%s" % endpoint]
        else:
            return ""

    @staticmethod
    def render_exist(endpoint):
        if "render_%s" % endpoint in Renderer._render:
            return True
        else:
            return False

    @staticmethod
    def print_table(header, list):
        size_cols = []
        line = '+'
        for i in range(0, len(header)):
            size_cols.append(len(header[i]) + 2)
        for element in list:
            for i in range(0, len(header)):
                if len(element[i]) + 2 > size_cols[i]:
                    size_cols[i] = len(element[i]) + 2
        for col in size_cols:
            line += '-' * col + '+'
        table = line + '\n|'
        for i in range(0, len(header)):
            table += " " + header[i] + (" " * (size_cols[i] - len(header[i]) - 1)) + "|"
        table += "\n" + line + "\n"
        for element in list:
            table += "|"
            for i in range(0, len(header)):
                table += " " + element[i] + (" " * (size_cols[i] - len(element[i]) - 1)) + "|"
            table += "\n"
        print(table + line + "\n")
