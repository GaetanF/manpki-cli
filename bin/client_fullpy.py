import requests_unixsocket

session = requests_unixsocket.Session()

# Access /ping from /tmp/manpki.cli.sock
r = session.get('http+unix://%2Ftmp%2Fmanpki.sock/ping')
print(r.content)
