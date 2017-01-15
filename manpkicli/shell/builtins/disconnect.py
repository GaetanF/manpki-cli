from ... import client
from ...constants import SHELL_STATUS_RUN


def disconnect(args):
    client.disconnect()
    return SHELL_STATUS_RUN
