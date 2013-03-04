#!/usr/bin/env python

# Make sure this code is in sync with the BTS directory.
# Fixes may need to be applied to both.

"""Start the process and dump the documentation to the doc dir."""

import socket
import subprocess
import time
import os
import sys

import osmoutil
import obscvty

def dump_doc(name, port, filename):
    vty = obscvty.VTYInteract(name, "127.0.0.1", port)
    xml = vty.command("show online-help")
    # Now write everything until the end to the file
    out = open(filename, 'w')
    out.write(xml)
    out.close()


"""Dump the config of all the apps.

Returns the number of apps configs could not be dumped for."""
def dump_configs():
    failures = 0

    for app in osmoutil.apps:
        appname = app[3]
        print "Starting app for %s" % appname
        proc = None
        cmd = [app[1], "-c", osmoutil.app_configs[appname][0]]
        try:
            proc = subprocess.Popen(cmd, stdin=None, stdout=None)
        except OSError: # Probably a missing binary
            print >> sys.stderr, "Skipping app %s" % appname
            failures += 1
        else:
            time.sleep(1)
            try:
                dump_doc(app[2], app[0], 'doc/%s_vty_reference.xml' % appname)
            except IOError: # Generally a socket issue
                print >> sys.stderr, "Couldn't connect to %s, skipping" % appname
                failures += 1
        finally:
            osmoutil.end_proc(proc)

    return failures


if __name__ == '__main__':
    num_failures = dump_configs()
    if num_failures > 0:
        print >> sys.stderr, "Warning: Skipped %s apps" % num_failures
    sys.exit(num_failures)

