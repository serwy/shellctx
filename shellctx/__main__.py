import os
import os.path
import platform
import runpy
import subprocess
import sys


ctx_globals = runpy.run_module('shellctx.ctx')

if platform.system() == 'Windows':
    if (ctx_home := os.environ.get('CTX_HOME')):
        ctx_tmp = ctx_home
    elif (home := os.environ.get('HOME')):
        ctx_tmp = f"{home}\\.ctx"
    elif (userprofile := os.environ.get('USERPROFILE')):
        ctx_tmp = f"{userprofile}\\.ctx"
    else:
        ctx_tmp = None

    if ctx_tmp and os.path.exists(ctx_export := f"{ctx_tmp}\\ctx_export.bat"):
        subprocess.run(ctx_export)
        os.replace(ctx_export, f"{ctx_tmp}\\last_export.bat")

retcode = ctx_globals.get('retcode', 0)
sys.exit(retcode)
