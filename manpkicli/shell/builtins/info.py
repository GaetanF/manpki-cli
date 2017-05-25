from ...client import client
from ...tools.render import Renderer
from ...constants import SHELL_STATUS_RUN


def info(args):
    data = client.get("/info")
    if Renderer.render_exist("manpki.server.info"):
        print(Renderer.render(data, "manpki.server.info"))
    else:
        print(data)
    return SHELL_STATUS_RUN
