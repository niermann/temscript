#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.sysconfig import get_python_inc
import glob
import os.path
import sys

# Read version
execfile('temscript/version.py')

def get_version():
    from temscript.instrument import version

if sys.platform == 'win32':
    # Only build _temscript c++ adapter on windows platforms
    py_includes = [os.path.join(get_python_inc(), '../Lib/site-packages/numpy/core/include/')]
    ext_modules = [Extension('_temscript', glob.glob(os.path.join('_temscript_module', '*.cpp')),include_dirs=py_includes)]
else:
    ext_modules = []

setup(name = 'temscript',
      version = __version__,
      description = 'TEM Scripting adapter for FEI microscopes',
      author = 'Tore Niermann',
      author_email = 'tore.niermann@tu-berlin.de',
      packages=['temscript'],
      requires = ['numpy', 'enum34'],
      ext_modules = ext_modules,
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Win32 (MS Windows)',
                     'Intended Audience :: Science/Research',
                     'Intended Audience :: Developers',
                     'Operating System :: Microsoft :: Windows',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Software Development :: Libraries'
                     'License :: OSI Approved :: BSD License'],
      platforms = ['win32'])
