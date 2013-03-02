#!/usr/bin/env python

"""Start the process and dump the documentation to the doc dir."""

import socket, subprocess, time, os, sys
import util, openbsc

def dump_doc(name, port, filename):
    vty = openbsc._VTYSocket(name, "127.0.0.1", port)
    xml = vty.command("show online-help")
    # Now write everything until the end to the file
    out = open(filename, 'w')
    out.write(xml)
    out.close()


# Dump the config of all our apps
def dump_configs():
    for app in util.apps:
        appname = app[3]
        print "Starting app for %s" % appname
        proc = None
        cmd = [app[1], "-c", util.app_configs[appname][0]]
        try:
            proc = subprocess.Popen(cmd, stdin=None, stdout=None)
        except OSError: # Probably a missing binary
            print >> sys.stderr, "Skipping app %s" % appname
        except IOError: # Generally a socket issue
            print >> sys.stderr, "Couldn't connect to %s, skipping" % appname
        else:
            time.sleep(1)
            try:
                dump_doc(app[2], app[0], 'doc/%s_vty_reference.xml' % appname)
            finally:
                util.endProc(proc)

if __name__ == '__main__':
    dump_configs()

