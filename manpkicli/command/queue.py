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

"""Queue management command line"""

from .. import shell

try:
    import argparse
    USING_ARGPARSE = True
except ImportError:
    import optparse
    USING_ARGPARSE = False

def main():
    if USING_ARGPARSE:
        parser = argparse.ArgumentParser(
            description='Launch Shell for ManPKI.')
    else:
        parser = optparse.OptionParser(
            description='Launch Shell for ManPKI.')
        parser.parse_args_orig = parser.parse_args

        def my_parse_args():
            res = parser.parse_args_orig()
            res[0].ensure_value('ips', res[1])
            return res[0]

        parser.parse_args = my_parse_args
        parser.add_argument = parser.add_option
    shell.launch()
