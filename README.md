
# shellctx

Shell context helper for saving, recalling, and executing information.

## Why?

Q: Shells provide alias capabilities and environment variables which 
   can do the same thing. Why this?

A: I don't want to edit `.bashrc` files to add or change aliases/variables. 
   I want state changes to be accessible from all open terminals without 
   sourcing shell files. Environment variables and aliases by themselves 
   are not persistent across restarts.


## Usage

The `ctx` command is the entry into the program. It behaves like a dictionary
that can get/set/delete keys and values.

    $ ctx set x 123
    $ ctx get x
    123

    $ ctx del x


By default, `ctx` shows the current context and the entries

    $ ctx
    Using context main
    There are 2 entries.

    2020-01-01T23:24:40.893719    server = python3 -m http.server
    2020-01-01T23:07:57.792251    home = /home/serwy

It can be used for storing a directory and later changing to it:

    $ cd /very/long/directory/to/type/manually
    $ ctx set project `pwd`

    $ cd `ctx get project`

It can be used to save and load environment variables:

    $ ctx set myshell $SHELL

    $ export SHELL=`ctx get myshell`

## Shell execution

A key's value can be passed directly to the shell:

    $ ctx set server  python3 -m http.server
    $ ctx shell server
    Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...


## Other commands

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


## Environment Variables

### `CTX_NAME`

The active context may be forced by setting the `CTX_NAME` environment variable.

This is useful when needing to dedicate a terminal to a particular context.


## Implementation details

The context dictionaries are stored in `~/.ctx/`
The `.json` files are the context dictionaries.
The `.log` files are the change logs.

The `_name.txt` contains the name of the active context.
If missing, defaults to `main`.


## Install

Ensure that the `ctx` script can be found on your system `PATH`,
e.g. `~/.local/bin`.

    pip3 install shellctx

or

    python3 setup.py install

If you just want the script directly, you can download and copy
`shellctx/ctx.py` as `ctx` somewhere on your `$PATH` and apply `chmod +x`.


## License

Licensed under the GNU General Public License, Version 3.0


## See also

* https://en.wikipedia.org/wiki/ISO_8601
* https://xkcd.com/1179/
