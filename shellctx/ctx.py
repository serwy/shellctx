#!/usr/bin/env python3
"""
shellctx
--------

Shell Context Helper

Web:      https://github.com/serwy/shellctx

Author:   Roger D. Serwy
Date:     2020-06-26
License:  GNU GPLv3, https://www.gnu.org/licenses/gpl-3.0.en.html


"""

import os
import sys
import json

__version__ = '0.1.2'

# ANSI coloring
color = {
    '': '\033[0m',  # reset
    'black': '\033[0;30m',
    'red': '\033[1;31m',
    'green': '\033[0;32m',
    'blue': '\033[1;94m',
}

if sys.platform.startswith('win'):
    color = dict.fromkeys(color.keys(), '')

def _print_version():
    s = ('shellctx version ',
         color['red'],
         __version__,
         color['']
         )
    print(''.join(s), file=sys.__stderr__)

env_name = os.environ.get('CTX_NAME')
verbose_flag = int(os.environ.get('CTX_VERBOSE', 0))


if verbose_flag:
    print('CTX_VERBOSE=%i' % verbose_flag, file=sys.__stderr__)
    _print_version()


import datetime
now = datetime.datetime.now().isoformat()


ctx_home = os.environ.get('CTX_HOME', None)
if ctx_home is None:
    ctx = os.path.expanduser('~/.ctx')
else:
    if verbose_flag:
        print('CTX_HOME=%s' % ctx_home, file=sys.__stderr__)
    ctx = ctx_home

os.makedirs(ctx, exist_ok=True)

# grab the pointer name
name_file = os.path.join(ctx, '_name.txt')
if os.path.exists(name_file):
    with open(name_file, 'r') as fid:
        name = fid.read().strip()
else:
    name = 'main'


if env_name:
    if verbose_flag:
        print('CTX_NAME=%s' % env_name, file=sys.__stderr__)
    name = env_name

ctx_file = os.path.join(ctx, name + '.json')
log_file = os.path.join(ctx, name + '.log')

if os.path.exists(ctx_file):
    with open(ctx_file, 'rb') as fid:
        data = fid.read()
        cdict = json.loads(data.decode('utf8'))
else:
    cdict = {}


def load_log():
    if os.path.exists(log_file):
        with open(log_file, 'rb') as fid:
            data = fid.read()
            log = json.loads(data.decode('utf8'))
    else:
        log = []
    return log



def _print_args():
    # debug, dump sys.argv
    print('sys.argv[:]', file=sys.__stderr__)
    for n, i in enumerate(sys.argv):
        s = (color['red'],
             '  %3i' % n,
             color[''],
             ' = ',
             color['blue'],
             repr(i),
             color[''],
             )
        print(''.join(s), file=sys.__stderr__)


if verbose_flag > 1:
    _print_args()
    print(file=sys.__stderr__)


cmd = None
key = None
value = None

retcode = 0

try:
    cmd = sys.argv[1]
    key = sys.argv[2]
    v = sys.argv[3]  # trigger error if missing
    value = ' '.join(sys.argv[3:])
except IndexError:
    pass

if verbose_flag > 1:
    s = ('processed arguments:\n',
         '    command:  %s\n' % repr(cmd),
         '    key:      %s\n' % repr(key),
         '    value:    %s\n' % repr(value)
         )
    print(''.join(s), file=sys.__stderr__)

    s = ('context home: %s\n' % ctx)
    print(''.join(s), file=sys.__stderr__, end='')

    s = ('context file: %s\n' % ctx_file)
    print(''.join(s), file=sys.__stderr__)


if cmd is None:
    cmd = '_fullitems'

need_store = False


if cmd == 'args':
    _print_args()

elif cmd == 'setpath':
    assert(key is not None)
    assert(value is not None)
    base = os.getcwd()
    if value == '.':  # . for pwd
        store = base
    else:
        store = os.path.join(base, value)

    # rewrite for the log
    cmd = 'set'
    value = store

    cdict[key] = (now, store)
    need_store = True

    s = (color['red'],
         key,
         color[''],
         '=',
         color['blue'],
         store,
         color[''],
         )
    print(''.join(s))

elif cmd == 'get':
    v = cdict[key][1]
    if sys.stdout.isatty():
        s = (color['green'],
            v,
            color[''],
            )
        print(''.join(s))
    else:
        print(v, end='')

elif cmd in ['shell', 'dryshell']:
    # use the key as the command
    # and the value as keys for the arguments
    sh = cdict[key][1]
    if value is None:
        arg = ''
    else:
        args = [cdict[v][1] for v in value.split()]
        arg = ' '.join(args)

    sh_cmd = sh
    if arg:
        sh_cmd = sh_cmd + ' ' + arg

    s = ('shell command: ',
        color['blue'],
        sh_cmd,
        color[''],
        )
    if verbose_flag:
        print(''.join(s), file=sys.__stderr__)

    if cmd == 'shell':
        os.system(sh_cmd)
    else:
        print('dryrun ' + ''.join(s))

elif cmd in ('exec', 'dryexec'):
    import shlex
    import subprocess

    sh = cdict[key][1]
    args = shlex.split(sh)
    args.extend(sys.argv[3:])

    s = ('exec command: ',
        color['blue'],
        repr(args),
        color[''],
        )
    if verbose_flag:
        print(''.join(s), file=sys.__stderr__)

    if cmd == 'exec':
        proc = subprocess.Popen(args)
        retcode = proc.wait()
    else:
        print('dryrun ' + ''.join(s))

elif cmd == '_pop':  # may remove
    print(cdict[key][1], end='')
    del cdict[key]
    need_store = True

elif cmd == 'set':
    assert(value is not None)
    cdict[key] = (now, value)
    need_store = True

elif cmd == 'del':
    del cdict[key]
    if value:
        # TODO: ensure all keys exist before
        # for deleting multiple keys
        for v in value.split():
            del cdict[v]
    need_store = True

elif cmd == 'keys':
    keys = sorted(cdict.keys())
    for k in keys:
        s = (color['red'],
            k,
            color[''],
            )
        print(''.join(s))

elif cmd == 'rename':
    assert(len(value.split()) == 1)
    v = cdict[key]
    cdict[value] = v
    del cdict[key]
    need_store = True

elif cmd == 'copy':
    assert(len(value.split()) == 1)
    v = cdict[key]
    cdict[value] = (now, v[1])
    need_store = True

elif cmd == 'items':
    # make the output resemble `env`
    keys = sorted(cdict.keys())
    for k in keys:
        s = (color['red'], k, color[''], '=',
             color['blue'],
             cdict[k][1],
             color['']
        )
        print(''.join(s))

elif cmd == '_fullitems':
    # timestamp, key, value
    everything = [(v[0], k, v[1]) for k, v in cdict.items()]
    x = sorted(everything, reverse=True)
    s = ('Using context ', color['blue'], name, color[''], '')
    if env_name:
        s = s + (' (set by CTX_NAME)', )
    if ctx_home:
        s = s + ((' (from CTX_HOME=%s)' % ctx_home),)
    print(''.join(s))
    s = ('There are ', color['blue'], str(len(everything)),
        color[''], ' entries.\n')
    print(''.join(s))

    for ctime, key, value in x:
        value=str(value)
        s = (color['green'],
             ctime, '    ',
             color['red'], key,
             color[''], ' = ',
             color['blue'], value,
             color['']
             )
        print(''.join(s))

elif cmd == 'log':
    log = load_log()
    for x in log:
        print(x)

elif cmd == 'switch':
    if key is None:
        # print all the context names
        f = os.listdir(ctx)
        ext = '.json'
        f = [i.rpartition(ext)[0] for i in f if i.endswith(ext)]
        if name not in f:
            f.append(name)
        for i in sorted(f):
            if i == name:
                s = (color['blue'],
                     '* ',
                     i,
                     color[''])
            else:
                s = ('  ', i)

            print(''.join(s))

    elif env_name:
        s = ('context set by CTX_NAME as ',
             color['blue'],
             env_name,
             color[''],
             '. Not switching.')
        print(''.join(s))

    else:
        if name != key:
            s = ('switching to "',
                color['blue'],
                key,
                color[''],
                '" from "',
                color['blue'],
                name,
                color[''],
                '"',
                )
            print(''.join(s))
            # switch to the context, if available
            with open(name_file, 'w') as fid:
                fid.write(key)
        else:
            s = ('already on "',
                color['blue'],
                key,
                color[''],
                '"',
                )
            print(''.join(s))

elif cmd == 'import':
    assert(key is not None)
    missing = object()
    env_value = os.environ.get(key, missing)
    store_as = key
    if value is not None:
        if len(value.split()) == 1:
            store_as = value
        else:
            raise ValueError('needs to be a single word')

    if env_value is not missing:
        cdict[store_as] = (now, env_value)
        need_store = True

elif cmd == 'update':
    # update the keys with the given file of key=value lines
    # example: $ env | ctx update -
    # the "items" command can be used to bulk transfer key-values
    #   ctx items > kv.txt
    #   ctx switch new_env
    #   ctx update kv.txt
    assert(key is not None)
    assert(value is None)
    # key is a file, - for stdin. readlines,
    if key == '-':
        fid = sys.stdin
    else:
        fid = open(key, 'r')

    # process the lines
    d = {}
    for line in fid.readlines():
        key, eq, value = line.partition('=')
        value = value.rstrip() # strip newline
        d[key] = (now, value)

    fid.close()
    # update if no error occurs
    cdict.update(d)
    need_store = True

    # FIXME: need to adjust the log data

elif cmd == 'clear':
    # require clear to have the key as a failsafe
    assert(key == name)
    cdict.clear()
    need_store = True

elif cmd == '_delctx':
    assert(key is not None)
    assert(value is None)
    _ctx_file = os.path.join(ctx, key + '.json')
    _log_file = os.path.join(ctx, key + '.log')
    if os.path.exists(_ctx_file):
        os.remove(_ctx_file)
    if os.path.exists(_log_file):
        os.remove(_log_file)

elif cmd == 'version':
    _print_version()

elif cmd == '_dict':
    end = '\n' if sys.stdout.isatty() else ''
    print(ctx_file, end=end)

elif cmd == '_download':
    # print out the download command, if running directly
    sh_cmd = ('curl '
              'https://raw.githubusercontent.com/serwy/shellctx/master/shellctx/ctx.py',
              ' -o ',
              sys.argv[0]
              )
    if __name__ == '__main__':
        end = '\n' if sys.stdout.isatty() else ''
        print(''.join(sh_cmd), end=end)
    else:
        s = ('running as a module ',
             color['red'],
             __name__,
             color[''],
             '\n',
             'from "%s"' % __file__,
             '\n'
             )
        print(''.join(s), file=sys.__stderr__)


elif cmd in ['help', '-h']:
    print('get set del shell exec items copy rename '
          'keys switch version log')

else:
    s = ('command not recognized: ', color['red'], cmd, color[''])
    print(''.join(s))


if need_store:
    with open(ctx_file, 'wb') as fid:
        fid.write(json.dumps(cdict, indent=4).encode('utf8'))

    log = load_log()
    log.append((now, cmd, key, value))

    with open(log_file, 'wb') as fid:
        fid.write(json.dumps(log, indent=4).encode('utf8'))

sys.exit(retcode)
