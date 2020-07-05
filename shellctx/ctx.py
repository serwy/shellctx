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

__version__ = '0.1.3'

# ANSI coloring
color = {
    '': '\033[0m',  # reset
    'black': '\033[0;30m',
    'red': '\033[0;31m',
    'green': '\033[0;32m',
    'blue': '\033[0;94m',
    'yellow': '\033[0;33m',
}


WINDOWS = False
if sys.platform.startswith('win'):
    WINDOWS = True
    color = dict.fromkeys(color.keys(), '')

if not sys.stdout.isatty():
    color = dict.fromkeys(color.keys(), '')

style = {
    '':color[''],  # blank
    'key': color['green'],
    'value': color['blue'],
    'time': color['red'],
    'command': color['blue'],
    'context': color['blue'],
}



def _print_version():
    s = ('shellctx version ',
         color['red'],
         __version__,
         color['']
         )
    print(''.join(s), file=sys.stderr)

env_name = os.environ.get('CTX_NAME')
verbose_flag = int(os.environ.get('CTX_VERBOSE', 0))


if verbose_flag:
    print('CTX_VERBOSE=%i' % verbose_flag, file=sys.stderr)
    _print_version()


import datetime
def get_now():
    now = datetime.datetime.now().isoformat()
    return now

now = get_now()

ctx_home = os.environ.get('CTX_HOME', None)
if ctx_home is None:
    ctx = os.path.expanduser('~/.ctx')
else:
    if verbose_flag:
        print('CTX_HOME=%s' % ctx_home, file=sys.stderr)
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
        print('CTX_NAME=%s' % env_name, file=sys.stderr)
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
    print('sys.argv[:]', file=sys.stderr)
    for n, i in enumerate(sys.argv):
        s = (style['key'],
             '  %3i' % n,
             color[''],
             ' = ',
             style['value'],
             repr(i),
             color[''],
             )
        print(''.join(s), file=sys.stderr)


if verbose_flag > 1:
    _print_args()
    print(file=sys.stderr)


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
    print(''.join(s), file=sys.stderr)

    s = ('context home: %s\n' % ctx)
    print(''.join(s), file=sys.stderr, end='')

    s = ('context file: %s\n' % ctx_file)
    print(''.join(s), file=sys.stderr)


if cmd is None:
    cmd = '_fullitems'

need_store = False
log_extra = []  # for extra logging information


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

    if WINDOWS:
        if ' ' in store:
            # double-quote the path due to spaces
            store = '"%s"' % store

    # rewrite for the log
    cmd = 'set'
    value = store

    cdict[key] = (now, store)
    need_store = True

    s = (style['key'],
         key,
         color[''],
         '=',
         style['value'],
         store,
         color[''],
         )
    print(''.join(s))

elif cmd == 'get':
    v = cdict[key][1]
    s = (style['value'],
        v,
        color[''],
        )
    print(''.join(s))

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
        style['command'],
        sh_cmd,
        color[''],
        )
    if verbose_flag:
        print(''.join(s), file=sys.stderr)

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
        style['command'],
        repr(args),
        color[''],
        )
    if verbose_flag:
        print(''.join(s), file=sys.stderr)

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
        s = (style['key'],
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
    # print out the items in creation order
    # if args, use args as keys

    # allow for `ctx items | ctx update -" to preserve time order
    x = ' '.join(sys.argv[2:])
    if x:
        keys = x.split()
        items = [
            (cdict[k][0], k, cdict[k][1])
            for k in keys
            ]
    else:
        everything = [(v[0], k, v[1]) for k, v in cdict.items()]
        items = sorted(everything)

    # make the output resemble `env`
    for ctime, _key, _value in items:
        s = (style['key'], _key, color[''], '=',
             style['value'],
             _value,
             color['']
        )
        print(''.join(s))

elif cmd == '_fullitems':
    # timestamp, key, value
    everything = [(v[0], k, v[1]) for k, v in cdict.items()]
    x = sorted(everything, reverse=True)
    s = ('Using context ', style['context'], name, color[''], '')
    if env_name:
        s = s + (' (set by CTX_NAME)', )
    if ctx_home:
        s = s + ((' (from CTX_HOME=%s)' % ctx_home),)
    print(''.join(s))
    s = ('There are ', style['value'], str(len(everything)),
        color[''], ' entries.\n')
    print(''.join(s))

    for ctime, _key, _value in x:
        value=str(value)
        s = (style['time'],
             ctime, '    ',
             style['key'], _key,
             color[''], ' = ',
             style['value'], _value,
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
                s = (style['value'],
                     '* ',
                     i,
                     color[''])
            else:
                s = ('  ', i)

            print(''.join(s))

    elif env_name:
        s = ('context set by CTX_NAME as ',
             style['context'],
             env_name,
             color[''],
             '. Not switching.')
        print(''.join(s))

    else:
        if name != key:
            s = ('switching to "',
                style['context'],
                key,
                color[''],
                '" from "',
                style['context'],
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
                style['context'],
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
    now2 = now
    for line in fid.readlines():
        _key, eq, _value = line.partition('=')
        _value = _value.rstrip() # strip newline
        d[_key] = (now2, _value)
        log_extra.append((now2, 'update_set', _key, _value))

        while True:  # ensure unique now
            _now2 = get_now()
            if _now2 != now2:
                now2 = _now2
                break

    fid.close()
    # update if no error occurs
    cdict.update(d)
    need_store = True

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

elif cmd == 'entry':
    # auto-increment the maximum suffix for a key
    assert(key is not None)
    assert(value is not None)
    # use key as a prefix
    prefix = key + '_'
    N = len(prefix)
    keys = list(cdict.keys())
    suffix = [i[N:] for i in keys if i.startswith(prefix)]

    nums = []
    for n in suffix:
        try:
            nums.append(int(n))
        except:
            pass

    if not nums:
        nums.append(0)

    next_num = max(nums) + 1

    key = prefix + ('%03i' % next_num)
    assert(key not in cdict)  # must be new key

    cdict[key] = (now, value)

    need_store = True

    s = (style['key'],
         key,
         color[''],
         '=',
         style['value'],
         value,
         color[''],
         )
    print(''.join(s))

elif cmd in ('dosvar', ):
    # export a key into windows shell
    assert(key is not None)
    store_as = key
    if value is not None:
         store_as = value
    tstamp, cvalue = cdict[key]
    d = ['set %s=%s' % (store_as, cvalue)]
    if store_as == 'cd':
        if cvalue[0] == '"':
            # unquote the file
            if os.path.isfile(cvalue[1:-1]):
                head, tail = os.path.split(cvalue[1:-1])
                cvalue = '"%s"' % head
        else:
            if os.path.isfile(cvalue):
                head, tail = os.path.split(cvalue)
                cvalue = head

        d.append('cd %s' % cvalue)

    xfile = os.path.join(ctx, 'ctx_export.bat')
    with open(xfile, 'w') as fid:
        fid.write('\r\n'.join(d))

elif cmd == 'now':
    # useful for appending to file names
    # make the time filesystem-safe and still iso8601 compliant
    n = now.replace(':', '')
    print(n)


elif cmd == '_dict':
    print(ctx_file)

elif cmd == '_download':
    # print out the download command, if running directly
    sh_cmd = ('curl '
              'https://raw.githubusercontent.com/serwy/shellctx/latest/shellctx/ctx.py',
              ' -o ',
              sys.argv[0]
              )
    if __name__ == '__main__':
        print(''.join(sh_cmd))
    else:
        s = ('running as a module ',
             color['red'],
             __name__,
             color[''],
             '\n',
             'from "%s"' % __file__,
             '\n'
             )
        print(''.join(s), file=sys.stderr)


elif cmd in ['help', '-h']:
    print('get set del shell exec items copy rename '
          'keys switch version log entry now')

else:
    s = ('command not recognized: ', color['red'], cmd, color[''])
    print(''.join(s))


if need_store:
    with open(ctx_file, 'wb') as fid:
        fid.write(json.dumps(cdict, indent=4).encode('utf8'))

    log = load_log()
    log.append((now, cmd, key, value))
    if log_extra:
        log.extend(log_extra)

    with open(log_file, 'wb') as fid:
        fid.write(json.dumps(log, indent=4).encode('utf8'))

sys.exit(retcode)
