
from shellctx import ctx


import unittest
import shutil
import os
import io
import json
import datetime
import tempfile



NOW_DT = datetime.datetime(1970, 1, 1, 0, 0, 0, 123456)
NOW = NOW_DT.isoformat()


class TestContext(unittest.TestCase):

    def setUp(self):
        TMP_DIR = tempfile.mkdtemp(prefix='test-relmod-')
        self.reset_output()
        self.environ = {'CTX_HOME':TMP_DIR}
        self._ctx_file = os.path.join(TMP_DIR, 'main.json')

        self.TMP_DIR = TMP_DIR

    def tearDown(self):
        shutil.rmtree(self.TMP_DIR)

    def reset_output(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def load_ctx(self, name):
        cfile = os.path.join(self.TMP_DIR, '%s.json' % name)
        with open(cfile, 'r') as fid:
            v = json.load(fid)
        return v

    def load_name(self):
        cfile = os.path.join(self.TMP_DIR, '_name.txt')
        if os.path.isfile(cfile):
            with open(cfile, 'r') as fid:
                return fid.read().strip()
        else:
            return 'main'


    def write_ctx(self, d, name='main'):
        f = os.path.join(self.TMP_DIR, '%s.json'% name)
        with open(f, 'w') as fid:
            json.dump(d, fid)


    def p(self):
        print(self.stdout.getvalue(), file=sys.stdout)
        print(self.stderr.getvalue(), file=sys.stderr)


    def test_no_args(self):
        status = ctx.context((), self.environ, self.stdout, self.stderr)

        out = self.stdout.getvalue()
        self.assertTrue('Using context' in out)
        self.assertTrue('main' in out)
        self.assertTrue('There are 0 entries.' in out)
        self.assertEqual(status, 0)


    def test_set_get(self):
        ctx.context(('ctx', 'set', 'abc', '123'), self.environ,
                    self.stdout, self.stderr)
        out = self.stdout.getvalue()
        self.assertEqual(out, '')


        self.reset_output()

        ctx.context(('ctx', 'get', 'abc'), self.environ,
                    self.stdout, self.stderr)

        out = self.stdout.getvalue()
        self.assertEqual(out, '123\n')

    @unittest.skip('needs error handling')
    def test_bad_get(self):
        status = ctx.context(('ctx', 'get', 'MISSING'), self.environ,
                    self.stdout, self.stderr)

        print(status)

    def test_set_del(self):
        ctx.context(('ctx', 'set', 'abc', '123'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW)

        self.reset_output()

        v = self.load_ctx('main')
        self.assertEqual(v, {'abc': [NOW, '123']})


        ctx.context(('ctx', 'del', 'abc'), self.environ,
                    self.stdout, self.stderr)

        out = self.stdout.getvalue()
        self.assertEqual(out, '')

        v = self.load_ctx('main')
        self.assertEqual(v, {})


    def test_now(self):
        ctx.context(('ctx', 'now'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW)
        out = self.stdout.getvalue()
        self.assertEqual(out, NOW.replace(':', '') + '\n')

        # TODO, add date, hour, minute, seconds,
        # (date, day, d)
        # (hour, h)
        # (minute, m)
        # (seconds, second, s)
        # (microsecond, microseconds, us, u)


    def test_version(self):
        ctx.context(('ctx', 'version'), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, '')

        err = self.stderr.getvalue()
        self.assertEqual(err, 'shellctx version %s\n' % ctx.__version__)

        # TODO: (version, -v)

    def test_keys(self):

        d = {'a': [NOW, 'aaa'],
             'b': [NOW, 'bbb'],
             }

        with open(self._ctx_file, 'w') as fid:
            json.dump(d, fid)


        ctx.context(('ctx', 'keys'), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, 'a\nb\n')


    def test_items(self):

        d = {'a': [NOW, 'aaa'],
             'b': [NOW, 'bbb'],
             }

        with open(self._ctx_file, 'w') as fid:
            json.dump(d, fid)


        ctx.context(('ctx', 'items'), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, 'a=aaa\nb=bbb\n')



    def test_clear(self):

        d = {'a': [NOW, 'aaa'],
             'b': [NOW, 'bbb'],
             }

        with open(self._ctx_file, 'w') as fid:
            json.dump(d, fid)

        ctx.context(('ctx', 'clear', 'main'), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        ctx.context(('ctx', 'keys'), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, '')

        # TODO: test clear without "main" to raise an error

    def test_args(self):
        ctx.context(('ctx', 'args', 'a0', 'a1'), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        # args is diagnostic, so data goes on stderr
        out = self.stdout.getvalue()
        err = self.stderr.getvalue()

        errlines = [i.strip() for i in err.split('\n')]
        self.assertTrue("1 = 'args'" in errlines)
        self.assertTrue("2 = 'a0'" in errlines)
        self.assertTrue("3 = 'a1'" in errlines)


    def test_fullitems(self):
        d = {'a': [NOW, 'aaa'],
             'b': ['1971' + NOW[4:], 'bbb'],
             }
        self.write_ctx(d)

        ctx.context(('ctx', ), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        # args is diagnostic, so data goes on stderr
        out = self.stdout.getvalue()
        err = self.stderr.getvalue()

        self.assertEqual(err, '')

        self.assertTrue('Using context main' in out)
        self.assertTrue('b = bbb' in out)
        self.assertTrue('a = a' in out)
        self.assertTrue(NOW in out)
        self.assertTrue('1971-01-01' in out)


    def test_rename(self):
        d = {'a': [NOW, 'aaa'],
             'b': ['1971' + NOW[4:], 'bbb'],
             }
        self.write_ctx(d)

        ctx.context(('ctx', 'rename', 'a', 'c'), self.environ,
                    self.stdout, self.stderr,
                    _color=False)

        v = self.load_ctx('main')

        self.assertTrue('c' in v)
        self.assertFalse('a' in v)

        d['c'] = d.pop('a')
        self.assertEqual(v, d)



    def test_copy(self):
        d = {'a': ['1900-01-01T00:00:00', 'aaa'],
             }
        self.write_ctx(d)

        ctx.context(('ctx', 'copy', 'a', 'c'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        v = self.load_ctx('main')

        self.assertTrue('c' in v)
        self.assertTrue('a' in v)

        self.assertEqual(v['c'][0], NOW)
        self.assertNotEqual(v['a'][0], NOW)


    def test_switch(self):
        ctx.context(('ctx', 'switch', 'other'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        name = self.load_name()

        self.assertEqual(name, 'other')


    def test_setpath(self):

        cwd = os.getcwd()
        ctx.context(('ctx', 'setpath', 'place', '.'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        v = self.load_ctx('main')

        self.assertEqual(v, {'place': [NOW, cwd]})


        # TODO `abspath`

    def test_import(self):
        # grab an environment variable

        env = self.environ.copy()
        env['USER'] = 'ctx_user'

        ctx.context(('ctx', 'import', 'USER'), env,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        v = self.load_ctx('main')

        self.assertEqual(v, {'USER': [NOW, 'ctx_user']})

    def test_import2(self):
        # grab an environment variable

        env = self.environ.copy()
        env['USER'] = 'ctx_user'

        ctx.context(('ctx', 'import', 'USER', 'user2'), env,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        v = self.load_ctx('main')

        self.assertEqual(v, {'user2': [NOW, 'ctx_user']})


    def test_update(self):

        # write key=value to a temp file, and import them
        ufile = os.path.join(self.TMP_DIR, 'stuff.txt')

        with open(ufile, 'w') as fid:
            fid.write(
"""A=1
B=2
C=3
""")
        ctx.context(('ctx', 'update', ufile), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        v = self.load_ctx('main')
        self.assertTrue('A' in v)
        self.assertTrue('B' in v)
        self.assertTrue('C' in v)

        # FIXME: test sys.stdin with "-"


    def test_log(self):
        ctx.context(('ctx', 'set', 'abc', '123'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)
        out = self.stdout.getvalue()
        self.assertEqual(out, '')


        self.reset_output()

        ctx.context(('ctx', 'log'), self.environ,
                    self.stdout, self.stderr)
        out = self.stdout.getvalue()
        self.assertEqual(
            out,
            "['1970-01-01T00:00:00.123456', 'set', 'abc', '123']\n"
            )

    def test_entry(self):
        ctx.context(('ctx', 'entry', 'note', 'a', 'b', 'c'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, 'note_001=a b c\n')

        self.reset_output()

        ctx.context(('ctx', 'get', 'note_001'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, 'a b c\n')

        self.reset_output()
        ctx.context(('ctx', 'entry', 'note', 'more'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, 'note_002=more\n')


    def test_exec(self):
        d = {'a': [NOW, 'aaa'],
             'b': [NOW, 'bbb'],
             }

        self.write_ctx(d, 'main')
        ctx.context(('ctx', 'dryexec', 'a', '1234'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, "dryrun exec command: ['aaa', '1234']\n")


    def test_shell(self):
        d = {'a': [NOW, 'aaa'],
             'b': [NOW, 'bbb'],
             }

        self.write_ctx(d, 'main')
        ctx.context(('ctx', 'dryshell', 'a', 'b'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, "dryrun shell command: aaa bbb\n")

        # FIXME: make the outputs between shell and exec similar
        # TODO: - as a prefix escapes processing ?

    def test_delctx(self):
        d = {'a': [NOW, 'aaa'],
             'b': [NOW, 'bbb'],
             }
        self.write_ctx(d, 'main')

        ctx.context(('ctx', '_delctx', 'main'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        self.reset_output()
        ctx.context(('ctx',), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertTrue('Using context' in out)
        self.assertTrue('main' in out)
        self.assertTrue('There are 0 entries.' in out)

    def test_pop(self):
        d = {'a': [NOW, 'aaa'],
             'b': [NOW, 'bbb'],
             }
        self.write_ctx(d, 'main')

        ctx.context(('ctx', '_pop', 'a'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, 'aaa')  # FIXME, add \n

        v = self.load_ctx('main')
        self.assertTrue('a' not in v)


    def test_name(self):
        ctx.context(('ctx', 'name'), self.environ,
                    self.stdout, self.stderr,
                    _now=NOW,
                    _color=False)

        out = self.stdout.getvalue()
        self.assertEqual(out, "main\n")



if __name__ == '__main__':
    unittest.main(verbosity=2)
