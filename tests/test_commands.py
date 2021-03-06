import unittest
import subprocess
import sys
import os
import re

class NonZeroExit(Exception):
    pass

class RegexEqual(object):
    def __init__(self, r):
        self.re = re.compile(r)
    
    def __eq__(self, x):
        return bool(self.re.search(x))

class CommandsTest(unittest.TestCase):
    def setUp(self):
        # re-use if already created
        self.zone = 'cli53.example.com'
        try:
            self._cmd('rrpurge', '--confirm', self.zone)
        except NonZeroExit:
            # domain does not exist
            self._cmd('create', self.zone)
            
    def tearDown(self):
        # clear up
        self._cmd('rrpurge', '--confirm', self.zone)
        
    def _cmd(self, cmd, *args):
        pargs = ('scripts/cli53', cmd) + args
        p = subprocess.Popen(pargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        if p.returncode:
            print >> sys.stderr, p.stderr.read()
            raise NonZeroExit
        return p.stdout.read()
        
    def test_rrcreate(self):
        self._cmd('rrcreate', self.zone, '', 'A', '10.0.0.1')
        self._cmd('rrcreate', self.zone, 'www', 'CNAME', 'cli53.example.com.', '-x 3600')
        self._cmd('rrcreate', self.zone, 'info', 'TXT', 'this is a "test"')
        
        output = self._cmd('export', self.zone)
        output = [ x for x in output.split('\n') if '10.0.0.1' in x or 'www' in x or 'TXT' in x ]
        
        self.assertEqual(
            [
                "@ 86400 IN A 10.0.0.1",
                'info 86400 IN TXT "this is a \\"test\\""',
                "www 3600 IN CNAME cli53.example.com.",
            ],
            output
        )
        
    def test_rrdelete(self):
        self._cmd('rrcreate', self.zone, '', 'A', '10.0.0.1')
        self._cmd('rrdelete', self.zone, '', 'A')
        
