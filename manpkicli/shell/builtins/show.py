from ...client import client
from ...tools import Command
from ...constants import SHELL_STATUS_RUN


def show(args):
    realcmd = "%s %s" % ("show", ' '.join(args))
    cmd = Command.search_command(realcmd, None)
    if cmd:
        print(cmd.execute(realcmd, client))
    else:
        print("Command not found")
    return SHELL_STATUS_RUN
