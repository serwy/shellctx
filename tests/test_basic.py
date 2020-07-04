"""

shellctx tests


"""

import sys
import importlib
import unittest
import os
import subprocess
import tempfile
import shutil

CTX_HOME = tempfile.mkdtemp(prefix='ctxtest_')
print('CTX_HOME=%s' % CTX_HOME, file=sys.stderr)

assert(os.path.isdir(CTX_HOME))

EXEC = (sys.executable, '-m', 'shellctx.ctx')


import shellctx

def run_shellctx(args=()):
    ex = EXEC + args
    env = {'CTX_HOME': CTX_HOME}
    res = subprocess.run(ex, env=env, capture_output=True)
    return res


class TestShell(unittest.TestCase):

    def setUp(self):
        r = run_shellctx()
        self.assertTrue(r.returncode == 0)

    def tearDown(self):
        if os.path.isdir(CTX_HOME):
            shutil.rmtree(CTX_HOME)

    def test_set_get(self):
        r = run_shellctx(('set', 'x', '123'))
        self.assertTrue(r.returncode == 0)
        r = run_shellctx(('get', 'x'))
        self.assertTrue(r.stdout == b'123\n')

    def test_set_del(self):
        r = run_shellctx(('set', 'x', '123'))
        self.assertTrue(r.returncode == 0)
        r = run_shellctx(('del', 'x'))
        self.assertTrue(r.returncode == 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

