from .formatter import SuperFormatter
from .render import Renderer
from .command import Command
from .client import Client
from .completer import BufferAwareCompleter

import socket


def is_valid_ip_address(address):
    return is_valid_ipv4_address(address) or is_valid_ipv6_address(address)


def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True
