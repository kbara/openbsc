# Copyright (C) 2012 Holger Hans Peter Freyther
# Copyright (C) 2013 Katerina Barone-Adesi
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# VTY helper code for OpenBSC
#
import socket

class VTYInteract(object):
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port

        self.socket = None
        self.norm_end = '\r\n%s> ' % self.name
        self.priv_end = '\r\n%s# ' % self.name


    def _close_socket(self):
        self.socket.close()
        self.socket = None


    def _is_end(self, text, ends):
        for end in ends:
            if text.endswith(end):
                return end
        return ""


    def _common_command(self, request, close=False, ends=None):
        if not ends:
            ends = [self.norm_end, self.priv_end]
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setblocking(1)
            self.socket.connect((self.host, self.port))
            self.socket.recv(4096)

        # Now send the command
        self.socket.send("%s\r" % request)
        res = ""
        end = ""

        # Unfortunately, timeout and recv don't always play nicely
        while True:
            data = self.socket.recv(4096)
            res = "%s%s" % (res, data)
            if not res: # yes, this is ugly
                raise IOError, "Failed to read data (did the app crash?)"
            end = self._is_end(res, ends)
            if end:
                break

        if close:
            self._close_socket()
        return res[len(request) + 2: -len(end)]


    # There's no close parameter, as close=True makes this useless
    def enable(self):
        self.command("enable")


    """Run a command on the vty"""
    def command(self, request, close=False):
        return self._common_command(request, close)


    """Run enable, followed by another command"""
    def enabled_command(self, request, close=False):
        self.enable()
        return self._common_command(request, close)


    """Verify, ignoring leading/trailing whitespace"""
    # inspired by diff -w, though not identical
    def w_verify(self, command, results, close=False, loud=True):
        return self.verify(command, results, close, loud, lambda x: x.strip())


    """Verify that a command has the expected results

    command = the command to verify
    results = the expected results [line1, line2, ...]
    close = True to close the socket after running the verify
    loud = True to show what was expected and what actually happend, stdout
    f = A function to run over the expected and actual results, before compare

    Returns True iff the expected and actual results match"""
    def verify(self, command, results, close=False, loud=True, f=None):
        res = self.command(command, close).split('\r\n')
        if f:
            res = map(f, res)
            results = map(f, results)

        if loud:
            if res != results:
                print "Rec: %s\nExp: %s" % (res, results)

        return res == results
