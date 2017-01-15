from ... import client
from ...constants import SHELL_STATUS_RUN


def connect(args):
    if client.is_connected():
        client.disconnect()
    if len(args) > 0:
        print(args[0])
        msg = client.connect(args[0])
    else:
        msg = client.connect(None, use_socket=True)
    if not msg:
        print("Unable to connect")
    return SHELL_STATUS_RUN
