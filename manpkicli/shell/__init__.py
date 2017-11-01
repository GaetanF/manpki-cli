import getpass
import platform
import readline
import shlex
import signal
import socket
import sys
import traceback

from ..constants import *
from ..client import client
from ..logger import log
from ..shell.builtins import *
from ..tools import Command, BufferAwareCompleter

# Hash map to store built-in function name and reference as key and value
built_in_cmds = {}


def tokenize(string):
    import re
    tmpstr = re.sub('\s?[a-zA-Z0-9]+="[^"]+"', '', string)
    tmpstr = re.sub('^[^ ]*\s?', '', tmpstr)
    if "=" in tmpstr:
        for element in tmpstr.split(" "):
            list_cut = element.split("=")
            log.info(list_cut)
            string = re.sub(element, '%s="%s"' % tuple(list_cut), string)
    list_token = list(shlex.shlex(string))
    return list_token


def preprocess(tokens):
    processed_token = []
    for token in tokens:
        # Convert $-prefixed token to value of an environment variable
        if token.startswith('$'):
            processed_token.append(os.getenv(token[1:]))
        else:
            processed_token.append(token)
    return processed_token


def handler_kill(signum, frame):
    raise OSError("Killed!")


def change_context(context):
    if context:
        log.debug('Change context to '+context)
    else:
        log.debug('Exit context')
    import builtins
    builtins.current_context = context
    return SHELL_STATUS_RUN


def execute(cmd_tokens):
    if cmd_tokens:
        # Extract command name and arguments from tokens
        cmd_name = cmd_tokens[0]
        cmd_args = cmd_tokens[1:]

        # If the command is a built-in command,
        # invoke its function with arguments
        if cmd_name in built_in_cmds:
            return built_in_cmds[cmd_name](cmd_args)

        if cmd_name in Command.get_all_context():
            return change_context(cmd_name)

        # Wait for a kill signal
        signal.signal(signal.SIGINT, handler_kill)
        cmd = Command.search_command(cmd_name + " "+' '.join(cmd_args), current_context)
        if cmd:
            try:
                print(cmd.execute(cmd_name + " "+' '.join(cmd_args), client))
            except:
                traceback.print_exc()
        else:
            print("Command not found")
    # Return status indicating to wait for next command in shell_loop
    return SHELL_STATUS_RUN


# Display a command prompt as `[<user>@<hostname> <dir>]$ `
def display_cmd_prompt():
    # Get user and hostname
    user = getpass.getuser()
    hostname = socket.gethostname()

    # Get base directory (last part of the curent working directory path)
    cwd = os.getcwd()
    base_dir = os.path.basename(cwd)

    # Use ~ instead if a user is at his/her home directory
    home_dir = os.path.expanduser('~')
    if cwd == home_dir:
        base_dir = '~'

    connected = "\033[91m"
    if client.is_connected():
        connected = "\033[92m"

    path = ""
    log.debug(__builtins__)
    import builtins
    if 'current_context' in __builtins__ and builtins.current_context:
        path = " \033[0m("+builtins.current_context+")"+connected

    # Print out to console
    return "%s[%s %s]%s$\033[0m " % (connected, client.get_servername(), base_dir, path)


def pre_shell():
    sys.stdout.write("Welcome to the ManPKI shell !\n")
    sys.stdout.flush()


def ignore_signals():
    # Ignore Ctrl-Z stop signal
    if platform.system() != "Windows":
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    # Ignore Ctrl-C interrupt signal
    #signal.signal(signal.SIGINT, signal.SIG_IGN)


def read_input():
    return input(display_cmd_prompt())


def shell_loop(signum=None, frame=None):
    status = SHELL_STATUS_RUN

    while status == SHELL_STATUS_RUN:

        # Ignore Ctrl-Z and Ctrl-C signals
        ignore_signals()

        try:
            # Read command input
            cmd = read_input()
            with open(HISTORY_PATH, 'a') as history_file:
                history_file.write(cmd + os.linesep)
            # Tokenize the command input
            cmd_tokens = tokenize(cmd)
            # Preprocess special tokens
            # (e.g. convert $<env> into environment value)
            cmd_tokens = preprocess(cmd_tokens)
            # Execute the command and retrieve new status
            status = execute(cmd_tokens)
        except EOFError:
            status = exit()
        except KeyboardInterrupt:
            sys.stdout.write('\n')
        except:
            _, err, _ = sys.exc_info()
            print(err)


# Register a built-in function to built-in command hash map
def register_command(name, func):
    built_in_cmds[name] = func


def exit(args=None):
    try:
        change_context(None)
        client.disconnect()
    except:
        print("Cannot propery disconnect from the server")
    return SHELL_STATUS_STOP


def end(args):
    if current_context:
        change_context(None)
        return SHELL_STATUS_RUN
    else:
        exit()


def help(args):
    enter_cmd = None
    if len(args) > 0:
        enter_cmd = ' '.join(args) + ' '
    allcmds = Command.get_commands_context(current_context)
    all_help_cmds = []
    help_cmds = []
    for cmd in built_in_cmds.keys():
        all_help_cmds.append(cmd)
    for cmd in allcmds:
        if cmd:
            all_help_cmds.append(cmd.get_command())
    for cmd in Command.get_all_context():
        if cmd:
            all_help_cmds.append(cmd)
    for cmd in all_help_cmds:
        if enter_cmd:
            if cmd.startswith(enter_cmd) and ' '.join(cmd.split(' ')[:enter_cmd.count(' ')+1]) not in help_cmds:
                help_cmds.append(' '.join(cmd.split(' ')[:enter_cmd.count(' ')+1]))
        elif cmd:
            help_cmd = cmd.split(' ')[0]
            if help_cmd not in help_cmds:
                help_cmds.append(help_cmd)
    # @TODO : add description for each help command
    print(*help_cmds, sep='\n')
    return SHELL_STATUS_RUN


def post_complete(substitution, matches, longest_match_length):
    curr_line = readline.get_line_buffer()
    maxlen=0
    for item in matches:
        if len(item)+1 > maxlen:
            maxlen=len(item)+1
    print("")
    for item in matches:
        if item != "" and item[0] != " ":
            item = " " + item + (" " * (maxlen - len(item)+1 + 10)) + "help"
        print(item)
    sys.stdout.write(display_cmd_prompt() + curr_line)
    sys.stdout.flush()
    readline.redisplay()


# Register all built-in commands here
def init():
    register_command("exit", exit)
    register_command("end", end)
    register_command("history", history)
    register_command("connect", connect)
    register_command("disconnect", disconnect)
    register_command("help", help)
    register_command("info", info)
    register_command("show", show)
    register_command("debug", debug)

    readline.set_history_length(1000)
    if os.path.exists(HISTORY_PATH):
        readline.read_history_file(HISTORY_PATH)
    readline.set_history_length(1000)

    readline.set_completer(BufferAwareCompleter.complete)
    readline.set_completion_display_matches_hook(post_complete)
    readline.parse_and_bind('tab: complete')


def main():
    # Init shell before starting the main loop
    init()
    pre_shell()
    #signal.signal(signal.SIGINT, signal.SIG_IGN)
    shell_loop()

if __name__ == "__main__":
    main()
