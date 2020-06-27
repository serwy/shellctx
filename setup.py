#!/usr/bin/env python
import os
import glob
from setuptools import setup

from shellctx._version import __version__

def get_dir(d):
    return glob.glob('%s/*' % d)

with open('README.md', 'rb') as fid:
    LONG_DESCRIPTION = fid.read().decode('utf8')


setup(name='shellctx',
      version=__version__,
      description='shell context helper',
      author='Roger D. Serwy',
      author_email='roger.serwy@gmail.com',
      url='http://github.com/serwy/shellctx',
      packages=['shellctx'],
      package_dir = {},
      package_data = {},
      include_package_data=False,
      scripts = get_dir('scripts'),
      license='GNU GPLv3',
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Topic :: System :: Shells',
          'Topic :: Utilities',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        ],
     )
