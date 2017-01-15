from __future__ import print_function
import socket

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect("/tmp/manpki.cli.sock")
s.send(b'GET /ping HTTP/1.0\r\n\r\n')
data = s.recv(1024)
print('received %s bytes' % len(data))
print(data)
s.close()
