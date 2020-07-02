@echo off
python -m shellctx.ctx %*

if defined USERPROFILE (set ctx_tmp=%USERPROFILE%\.ctx)
if defined HOME (set ctx_tmp=%HOME%\.ctx)
if defined CTX_HOME (set ctx_tmp=%CTX_HOME%)

if defined ctx_tmp (
    if exist %ctx_tmp%\ctx_export.bat (
        %ctx_tmp%\ctx_export.bat > nul
        move /y %ctx_tmp%\ctx_export.bat %ctx_tmp%\last_export.bat > nul
    )
    set ctx_tmp=
)


