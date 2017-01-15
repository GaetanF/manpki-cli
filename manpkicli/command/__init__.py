#! /usr/bin/env python

# This file is part of ManPKI.
# Copyright 2016 Gaetan FEREZ <gaetan@ferez.fr>
#
# ManPKI is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ManPKI is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ManPKI. If not, see <http://www.gnu.org/licenses/>.

"""This sub-module contains functions to implement manpki.cli commands."""

__all__ = [
    'service',
    'check',
    'queue',
    'shell'
]


def get_command(name):
    if name in __all__:
        return getattr(__import__("%s.%s" % (__name__, name)), name).main


def guess_command(name):
    if name in __all__:
        return [name]
    possible = [cmd for cmd in __all__ if cmd.startswith(name)]
    if possible:
        return possible
    else:
        return [];
