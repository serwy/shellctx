
# shellctx

Shell context helper for saving, recalling, and executing information from
a persistent dictionary.


## Motivation

Setting environment variables and aliases (`.bashrc`, `.cshrc`, etc.)
is useful when you have an established workflow with known common actions.
This program is for discovering what that workflow should be, when the needed
working directories and commands are not fully known just yet. All shell
instances have access to the work-in-progress context dictionary.


## Usage

The `ctx` command is the entry into the program. It behaves like a dictionary
that can get/set/delete keys and values.

    $ ctx set x 123
    $ ctx get x
    123

    $ ctx del x

It can be used for storing a long directory for later use:

    $ cd /very/long/directory/to/type/manually
    $ ctx set project `pwd`

    $ cd `ctx get project`

It can store long commands for later use:

    $ ctx set server '/usr/bin/python3 -m http.server'
    $ ctx shell server
    Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...


It can also save and load environment variables:

    $ ctx set mypath $PATH
    $ export PATH=`ctx get mypath`

By default, `ctx` shows the current context dictionary and the
sorted timestamped entries:

    $ ctx
    Using context main
    There are 2 entries.

    2020-01-01T23:24:40.893719    server = python3 -m http.server
    2020-01-01T23:07:57.792251    home = /home/serwy


## Available Commands

`copy` - copies a key, updates timestamp

    $ ctx copy home home2

`rename` - renames a key, preserves timestamp

    $ ctx rename home2 home3

`items` - provides a sort-by-key display of key-values

    $ ctx items
    home=/home/serwy
    server=python3 -m http.server

`keys` - provides a list of keys

    $ ctx keys
    home
    server

`log` - print out a log of changes to the context dictionary

    $ ctx log
    ['2020-01-01T22:51:50.180685', 'set', 'home', '/home/serwy']
    ['2020-01-01T22:52:01.008981', 'copy', 'home', 'home2']
    ['2020-01-01T22:52:08.194826', 'rename', 'home2', 'home3']


`switch` - switch the context dictionary, or print a list.
New contexts may be created this way.

    $ ctx switch dev
    switching to "dev" from "main"

    $ ctx switch
    * dev
      main

`shell` - uses the key as a command, and values are treated as
additional keys. The command string is passed to a shell.

    $ ctx set port 9999
    $ ctx shell server port
    Serving HTTP on 0.0.0.0 port 9999 (http://0.0.0.0:9999/) ...

`dryshell` - prints the command passed to the shell without executing

    $ ctx dryshell server port
    dryrun shell command: python3 -m http.server 9999

`exec` - uses the key to get the executable, and the additional arguments
are passed directly to the executable.

    $ ctx exec server 9999
    Serving HTTP on 0.0.0.0 port 9999 (http://0.0.0.0:9999/) ...

`dryexec` - prints the arguments passed to the executable without executing.

    $ ctx dryexec server 9999
    dryrun exec command: ['python3', '-m', 'http.server', '9999']

`set` - set a key to a value

    $ ctx set keyname value

`get` - print the value for the given key

    $ ctx get server
    python3 -m http.server

`del` - delete a key

    $ ctx del keyname

`setpath` - add the present working directory to the value when setting
the given key

    $ ctx setpath keyname .bashrc
    keyname=/home/serwy/.bashrc

`args` - print out the arguments as seen by the program, quoted

    $ ctx args some arguments "kept together"
    sys.argv[:]
        0 = '/home/serwy/.local/bin/ctx'
        1 = 'args'
        2 = 'some'
        3 = 'arguments'
        4 = 'kept together'

## Environment Variables

### `CTX_NAME`

The active context may be forced by setting the `CTX_NAME` environment variable.

This is useful when needing to dedicate a terminal to a particular context.

### `CTX_VERBOSE`

A flag to increase verbosity. It is an integer value of `0`, `1`, or more.
If undefined, it defaults to `0`.

### `CTX_HOME`

Set the directory containing the dictionaries and logs. If unset,
it defaults to `~/.ctx/`.

## Implementation details

The context dictionaries are stored in `~/.ctx/`
The `.json` files are the context dictionaries.
The `.log` files are the change logs.

The `_name.txt` file contains the name of the active context.
If missing, defaults to `main`.


## Install

Ensure that the `ctx` script can be found on your system `PATH`,
e.g. `~/.local/bin`.

    pip3 install shellctx

or

    python3 setup.py install

If you just want the script directly, you can download and copy
`shellctx/ctx.py` as `ctx` somewhere on your `$PATH` and apply `chmod +x`.
The direct link is: https://raw.githubusercontent.com/serwy/shellctx/master/shellctx/ctx.py

    curl  https://raw.githubusercontent.com/serwy/shellctx/master/shellctx/ctx.py > ctx
    chmod +x ctx

## License

Licensed under the GNU General Public License, Version 3.0


## See also

* https://en.wikipedia.org/wiki/ISO_8601
* https://xkcd.com/1179/
