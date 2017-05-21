from ...client import client
from ...constants import SHELL_STATUS_RUN


def info(args):
    print(client.get("/info"))
    return SHELL_STATUS_RUN
