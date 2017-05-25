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
