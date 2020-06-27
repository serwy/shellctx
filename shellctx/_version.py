
# grab the version from ctx.py

import os
head, tail = os.path.split(__file__)

target = os.path.join(head, 'ctx.py')

with open(target, 'r') as fid:
    lines = fid.readlines()

for line in lines:
    if line.startswith('__version__'):
        exec(line)
        break

else:
    raise ValueError('version not found')
