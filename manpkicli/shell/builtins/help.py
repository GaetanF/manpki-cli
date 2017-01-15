from ...tools import Command
from ...constants import SHELL_STATUS_RUN


def help(args):
    print(Command.get_commands_current_context())
    return SHELL_STATUS_RUN
