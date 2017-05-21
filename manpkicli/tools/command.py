import re
import shlex
from ..logger import log
from .render import Renderer


class Command:
    _url = None
    _method = None
    _params = None
    _context = None
    _path = None
    _endpoint = None

    type_data = {
        "str": "[^ ]+",
        "int": "[0-9]*",
        "mail": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    }

    _listcmds = []
    _all_contexts = []

    def __init__(self, path, url, method, endpoint, context=None, params=None):
        self._url = url
        self._path = path
        self._method = method
        self._endpoint = endpoint
        self._context = context
        self._params = params

    def get_context(self):
        return self._context

    def get_command(self):
        return self._path

    def get_method(self):
        return self._method

    def get_function(self):
        return self._function

    @staticmethod
    def get_all_context():
        return Command._all_contexts

    def __repr__(self):
        return "<Command cmd: {}, url: {}, method: {}, context: {}, endpoint: {}, params: {}>".format(
            self._path,
            self._url,
            self._method,
            self._context,
            self._endpoint,
            self._params
        )

    def has_enough_data(self, data):
        if data and self._params:
            for param in self._params:
                if param['mandatory'] and (
                        param['name'] not in data.keys() or not re.match(self.type_data[param['type']], data[param['name']])):
                    return False
                elif param['name'] in data.keys() and not re.match(self.type_data[param['type']], data[param['name']]):
                    return False
        return True

    def execute(self, cmdargs, client):
        (url, data) = self._parse_cmd(cmdargs)
        if self.has_enough_data(data):
            log.debug(url)
            log.debug(data)
            if self._method == "GET":
                body = client.get(url)
            elif self._method == "PUT":
                body = client.put(url, data=data)
            elif self._method == "POST":
                body = client.post(url, data=data)
            else:
                body = None
                log.debug('Method not implemented')
        else:
            body = "Missing parameter"

        if body and body != 'You are disconnected !':
            if Renderer.render_exist(self._endpoint):
                return Renderer.render(body, self._endpoint)
            else:
                return body
        else:
            return None

    def _parse_cmd(self, cmdargs):
        cmd = self._path
        cleancmd = cmd.replace(' [param]', '').replace(' [param=value]', '')
        args = cmdargs.replace(cleancmd, '')
        lexer = shlex.shlex(args)
        param = []
        listLexer = list(lexer)
        # log.info("List Lexer : ")
        # log.info(listLexer)
        if '=' in listLexer:
            for i in range(0, len(listLexer)):
                if listLexer[i] == '=' and i >= 1:
                    param.append({listLexer[i - 1]: shlex.split(listLexer[i + 1])[0]})
                    args = args.replace(listLexer[i - 1] + " = " + listLexer[i + 1], "")
        lexer = shlex.shlex(args)
        listLexer = list(lexer)
        for i in range(0, len(listLexer)):
            param.append(listLexer[i])
            args = args.replace(listLexer[i], "")
        data = None
        log.debug(self._method)
        log.debug(len(param))
        log.debug(param)
        pattern = re.compile("<[^>]*>")
        if self._method == 'GET':
            if len(param) == 0:
                url = re.sub(pattern, '', self._url)
            else:
                url = self._url
                for paramurl in re.findall(pattern, url):
                    url = url.replace(paramurl, param.pop(0))
        else:
            url = re.sub(pattern, '', self._url)
            data = param
        log.debug(url)
        log.debug(data)
        formateddata = {}
        if data:
            for p in data:
                fdata = p
                if p.__class__.__name__ == 'str':
                    fdata = {p: True}
                log.info(fdata)
                formateddata.update(fdata)
        else:
            formateddata = data
        log.debug(formateddata)
        return url, formateddata

    @staticmethod
    def build_all_context():
        Command._all_contexts = []
        for cmd in Command._listcmds:
            if cmd.get_context() not in Command._all_contexts:
                Command._all_contexts.append(cmd.get_context())

    @staticmethod
    def add(path, url, method, context, endpoint=None, params=None):
        Command._listcmds.append(Command(
            path=path,
            url=url,
            method=method,
            endpoint=endpoint,
            params=params,
            context=context
        ))

    @staticmethod
    def get_commands_context(context):
        allcmdincontext = []
        for cmd in Command._listcmds:
            if cmd.get_context() == context or cmd.get_context() == None:
                allcmdincontext.append(cmd)
        return allcmdincontext

    @staticmethod
    def get_url_of_command(command):
        pass

    @staticmethod
    def search_command(command, context):
        listcmd = command.split(' ')
        sizearray = len(listcmd)
        for x in reversed(range(0, sizearray + 1)):
            testcmd = ' '.join(listcmd[:x])
            for cmd in Command._listcmds:
                if cmd.get_context() == context or not cmd.get_context():
                    thecmd = cmd.get_command().replace('[param]', '[a-zA-Z0-9]*')
                    thecmd = thecmd.replace('[param=value]', '(\s?(?:[a-zA-Z0-9]*)\s=\s"(.+?)")+')
                    log.debug("Testcmd : '%s'" % testcmd)
                    log.debug("Get cmd : '%s'" % thecmd)
                    match = re.search("^%s$" % thecmd, testcmd)
                    if match:
                        return cmd
        return None

    @staticmethod
    def build_all_commands_from_api(commands):
        if 'api' in commands:
            for command in commands['api']:
                Command.add(
                    path=command['command'],
                    url=command['url'],
                    method=command['method'],
                    endpoint=command['endpoint'],
                    context=command['context'],
                    params=command['args']
                )

    @staticmethod
    def get_commands():
        return Command._listcmds

    @staticmethod
    def build(commands):
        Command._all_contexts = []
        Command._listcmds = []
        log.debug(commands)
        Command.build_all_commands_from_api(commands)
        Command.build_all_context()
        log.debug(Command._all_contexts)
        log.debug(Command._listcmds)
