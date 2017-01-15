from manpkicli import config

import urllib
import sys
import os
import string
from scp import SCPClient
from paramiko import SSHClient


IDENTCHARS = string.ascii_letters + string.digits + '_'


class Copy:

    def report_http_progress(self, blocknr, blocksize, size):
        current = blocknr*blocksize
        sys.stdout.write("\rDownloading : {0:.2f}%".format(100.0*current/size))
        if current/size == 1:
            sys.stdout.write("\rDownloading : done\n")

    def copy_ftp_to_tmp(self, uri):
        urllib.urlretrieve(uri.geturl(), self.tmp_file.name, self.report_http_progress)

    def copy_ssh_to_tmp(self, uri):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        print(uri.username)
        if not uri.username:
            ssh.connect(uri.hostname, allow_agent=True)
        elif uri.username  and not uri.password:
            ssh.connect(uri.hostname, username=uri.username, allow_agent=True)
        elif uri.username and uri.password:
            ssh.connect(uri.hostname, username=uri.username, password=uri.password, allow_agent=True)

        # SCPCLient takes a paramiko transport as its only argument
        scp = SCPClient(ssh.get_transport())
        scp.get(uri.path, self.tmp_file.name)
        scp.close()

    def copy_http_to_tmp(self, uri):
        urllib.urlretrieve(uri.geturl(), self.tmp_file.name, self.report_http_progress)

    def copy_file_to_tmp(self, uri):
        shutil.copy2(uri.path, self.tmp_file.name)

    def copy_tmp_to_ftp(self, uri):
        session = ftplib.FTP(uri.hostname)

        if uri.username  and not uri.password:
            session.login(uri.username)
        elif uri.username and uri.password:
            session.login(uri.username, uri.password)

        if os.path.dirname(uri.path):
            session.cwd(os.path.dirname(uri.path))

        session.storbinary('STOR ' + os.path.basename(uri.path), self.tmp_file)

    def copy_tmp_to_ssh(self, uri):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        print(uri.username)
        if not uri.username:
            ssh.connect(uri.hostname, allow_agent=True)
        elif uri.username  and not uri.password:
            ssh.connect(uri.hostname, username=uri.username, allow_agent=True)
        elif uri.username and uri.password:
            ssh.connect(uri.hostname, username=uri.username, password=uri.password, allow_agent=True)

        # SCPCLient takes a paramiko transport as its only argument
        scp = SCPClient(ssh.get_transport())
        scp.put(self.tmp_file.name, uri.path)
        scp.close()

    def copy_tmp_to_file(self, uri):
        shutil.copy2(self.tmp_file.name, uri.path)

    def __init__(self, source, dest):
        self.methods_in = {
            'ftp' : self.copy_ftp_to_tmp,
            'ssh' : self.copy_ssh_to_tmp,
            'http': self.copy_http_to_tmp,
            'file': self.copy_file_to_tmp
        }

        self.methods_out = {
            'ftp' : self.copy_tmp_to_ftp,
            'ssh' : self.copy_tmp_to_ssh,
            'file': self.copy_tmp_to_file
        }
        self.tmp_file = tempfile.NamedTemporaryFile()

        source_uri = urlparse.urlparse(source)
        try:
            self.methods_in[source_uri.scheme](source_uri)
        except KeyError:
            print(exceptions.ProtocolException("Unknown protocol"))
        except Exception as e:
            print(e)

        dest_uri = urlparse.urlparse(dest)
        try:
            tmp_func = self.methods_out[dest_uri.scheme]
            tmp_func(dest_uri)
        except KeyError:
            print(exceptions.ProtocolException("Unknown protocol"))

        self.tmp_file.close()


class Show:

    base_dir = config.guess_prefix("shell")
    identchars = IDENTCHARS
    list_functions = []

    def __init__(self, line):
        self.load_functions()
        if "?" in line:
            self.show_help(line)
        else:
            self.call_command(self.parse_line(line))

    def parse_line(self, line):
        arg_path = line.split(" ")
        if arg_path and len(arg_path)>0:
            command = 'show_' + '_'.join(arg_path)
            orig_command = command
            while not hasattr(self, command.lower()) and command != "show":
                command = "_".join(command.split("_")[:-1])
            if command == "show":
                print("% Undefine command")
                return "show_help"
            if not orig_command == command:
                command += "~" + orig_command.replace(command, "")[1:]
        else:
            command = None
        return command

    def call_command(self, command):
        try:
            args = None
            if '~' in command:
                (command, args) = command.split('~')

            if args:
                if config.DEBUG:
                    print("SHOW Call : " + command)
                    print("SHOW Args : " + args)
                getattr(self, command.lower())(args)
            else:
                if config.DEBUG:
                    print("SHOW Call : " + command)
                getattr(self, command)()
        except AttributeError:
            print("% Invalid input detected")
        except TypeError as e:
            print('% Type "show ?" for a list of subcommands')

    def show_help(self, line=None):
        list_cmd = []
        list_help = []
        search_func = "show_"
        if line and not "?" in line[0] and line.endswith("?"):
            search_func += '_'.join(line.replace("?","").strip().lower().split(" ")) + "_"
        for func in self.__class__.__dict__.keys():
            if func.startswith(search_func) and not func.endswith("_help") and not "_" in func[len(search_func):]:
                list_cmd.append(func[len(search_func):])
                if hasattr(self, func + "_help"):
                    with Capturing() as output:
                        getattr(self, func + "_help")()
                    list_help.append(output[0])
                else:
                    list_help.append("")
        if len(list_cmd)>0:
            print("\n".join("{0}\t{1}".format(a, b) for a, b in zip(list_cmd, list_help)))
        if not search_func == "show_":
            if hasattr(self, search_func[:-1]):
                print("<cr>")
            else:
                print("% Invalid input detected")

    def show_config(self):
        for section in Config().config.sections():
            print(section)
            for option in Config().config.options(section):
                print(" ", option, "=", Config().config.get(section, option))

    def load_functions(self):
        if os.path.isdir(self.base_dir) and len(Show.list_functions) == 0:
            for dirpath,dirnames,filenames in os.walk(self.base_dir):
                for name in filenames:
                    if name.startswith("Sh") and name.endswith(".py"):
                        module_name = splitext(name)[0]
                        path = dirpath.replace(self.base_dir, "")[1:]
                        module_path = "Shell."
                        if len(path)>0:
                            module_path += '.'.join(path.split("/")).title() + "." + module_name
                        else:
                            module_path += module_name
                        import_str = "from " + module_path + " import " + module_name
                        if config.DEBUG:
                            print("Import all sub show from file " + name + " : " + import_str)
                        exec(import_str)
                        modul = sys.modules[module_path]
                        for func_name in getattr(modul, module_name).__dict__.keys():
                            if func_name.startswith("show_"):
                                Show.list_functions.append([modul, module_name, func_name])
                                setattr(self.__class__, func_name, self._make_show_cmd(modul, module_name, func_name))

    @staticmethod
    def _make_show_cmd(modul, module_name, func_name):
        def handler_show(self, args=None):
            try:
                class_inst = getattr(modul, module_name)(False)
                attr = getattr(class_inst, func_name)
                if args:
                    attr(args)
                else:
                    attr()
            except Exception as e:
                print('*** error:', e)
        return handler_show
