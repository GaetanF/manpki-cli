import os
import pwd
import stat
import requests
import requests_unixsocket
import json
import getpass
from jose import jws
from ..constants import *
from ..logger import log
from ..tools import Renderer, Command


def get_socket_file(paths=None):
    """Generates (yields) the available config files, in the correct order."""
    if DEBUG:
        log.debug("Get socket file")
    if paths is None:
        paths = [os.path.join(path, 'manpki.sock')
                 for path in ['/var/run/manpkid', '/var/run', '/tmp',
                              '/var/tmp/manpkid', './']]
    for path in paths:
        if os.path.exists(path) and stat.S_ISSOCK(os.stat(path).st_mode):
            return path


class Client:
    conn = None
    serverName = None
    userName = None
    path = None
    url = None
    use_socket = False

    _logged = False
    _cookies = None
    _secret = None
    _token = None

    def __init__(self):
        pass

    def is_connected(self):
        if self.conn:
            return True
        else:
            return False

    def is_logged(self):
        return self._logged

    def get_servername(self):
        if self.is_connected():
            return "%s@%s" % (self.userName, self.serverName)
        else:
            return "disconnected"

    def disconnect(self):
        if self.conn:
            self.conn.get(self._get_url("/logout"), cookies=self._cookies)
            self.conn.close()
        self.conn = None
        self._secret = None
        self._cookies = None
        self._token = None

    def _get_headers(self):
        headers = {
            "User-Agent": "ManPKIShell/1.0",
            "Authorization": "%s %s" % ("ManPKI", self._token)
        }
        return headers

    def _get_url(self, path):
        if self.use_socket:
            host = requests.compat.quote_plus(self.path)
            prefix = "http+unix"
            port = ""
        else:
            host = self.serverName
            prefix = "http"
            port = ":" + str(DEFAULT_PORT)

        if not path.startswith("/"):
            path = "/" + path
        return "%s://%s%s%s" % (prefix, host, port, path)

    def _build_env_(self):
        discoveryapi = self.get("/discovery")
        log.info(discoveryapi)
        lang = os.getenv('LANG')
        if not lang:
            lang = "en_FR.UTF-8"
        locales = self.get("/locale/%s" % lang)
        log.info(locales)
        render = self.get("/render")
        log.info(render['render'])
        Renderer.load_render(render['render'])
        Command.build(discoveryapi)
        return True

    def login(self):
        if self.use_socket:
            r1 = self.conn.get(self._get_url("/login"), auth=(self.userName, 'null'), cookies=self._cookies)
        else:
            thepass = getpass.getpass("Password : ")
            r1 = self.conn.get(self._get_url("/login"), auth=(self.userName, thepass), cookies=self._cookies)
        if r1.status_code == 200:
            decoded = self._decode_response(r1.content)
            self._token = decoded['token']
            return self._build_env_()
        elif r1.status_code == 403:
            print("User or password not valid")
        else:
            print("Error")
        self.disconnect()
        return False

    def connect(self, server, use_socket=False):
        self.use_socket = use_socket
        self.conn = None
        self._cookies = None
        self._secret = None
        if use_socket:
            self.userName = pwd.getpwuid(os.getuid())[0]
            self.serverName = "local"
            self.path = get_socket_file()
            self.url = self._get_url("/")
            self.conn = requests_unixsocket.Session()
        else:
            self.userName = server.split('@')[0]
            self.serverName = server.split('@')[1]
            self.path = None
            self.url = self._get_url("/")
            self.conn = requests.Session()

        r1 = self.conn.get(self._get_url("/ping"), cookies=self._cookies)
        self._cookies = r1.cookies
        if r1.status_code == 200:
            self._secret = json.loads(r1.content)['secret']
            return self.login()
        else:
            self.disconnect()
            return False

    def _decode_response(self, content):
        data = json.loads(content)
        signed = jws.verify(data, self._secret, algorithms=['HS256'])
        decoded = json.loads(signed.decode("utf8"))
        print(json.dumps(decoded, sort_keys=True, indent=4, separators=(',', ': ')))
        return decoded

    def query(self, verb, path, data=None):
        if self.is_connected():
            r = requests.Request(verb, self._get_url(path), json=data, headers=self._get_headers(),
                                 cookies=self._cookies)
            prepped = self.conn.prepare_request(r)
            r1 = self.conn.send(prepped)
            if r1.status_code == 200:
                return self._decode_response(r1.content)
            elif r1.status_code == 401:
                self.disconnect()
                return "You are disconnected !"
            else:
                print("Remote error : %s" % self._decode_response(r1.content)['error'])
                return None
        else:
            return "You are disconnected !"

    def get(self, path):
        return self.query("GET", path)

    def post(self, path, data):
        return self.query("POST", path, data)

    def put(self, path, data):
        return self.query("PUT", path, data)

    def delete(self, path, data):
        return self.query("DELETE", path, data)