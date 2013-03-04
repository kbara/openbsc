#!/usr/bin/env python

# (C) 2013 by Katerina Barone-Adesi <kat.obsc@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import traceback
import time

import obscvty
import osmoutil

def setup():
    cmd = ["./src/osmo-nitb/osmo-nitb", "-c", "doc/examples/osmo-nitb/hsl/openbsc.cfg"]
    test_proc = osmoutil.popen_devnull(cmd)
    time.sleep(1)
    test_vty = obscvty.VTYInteract("OpenBSC", "127.0.0.1", 4242)
    return test_proc, test_vty


def teardown(proc):
    osmoutil.end_proc(proc)


def run_tests(tests):
    passed_tests = []
    failed_tests = []
    exit_code = 0

    test_proc = None
    test_vty = None

    for test in tests:
        try:
            test_proc, test_vty = setup()
            test(test_vty)
        except Exception as e:
            print traceback.format_exc()
            failed_tests.append(test)
        else:
            passed_tests.append(test)
        finally:
            teardown(test_proc)

    print "%s tests passed" % len(passed_tests)
    if failed_tests:
        exit_code = 1
        print "%s tests failed" % len(failed_tests)
        for ft in failed_tests:
            print ft.__name__
    return exit_code


def test_history(vty):
    t1 = "show version"
    vty.command(t1)
    test_str = "show history"
    assert(vty.w_verify(test_str, [t1]))


def test_unknown_command(vty):
    test_str = "help show"
    assert(vty.verify(test_str, ['% Unknown command.']))


def test_terminal_length(vty):
    test_str = "terminal length 20"
    assert(vty.verify(test_str, ['']))


def test_fail(vty):
    test_str = "terminal length 20"
    assert(vty.verify(test_str, ["not really there"]))


tests = [test_terminal_length, test_unknown_command, test_history]

if __name__ == '__main__':
    import sys
    if sys.argv[1:] and sys.argv[1] in ["--include-framework-fail", "-z"]:
        tests.append(test_fail)

    sys.exit(run_tests(tests))

