#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.sysconfig import get_python_inc
import glob
import os.path
import sys

# Read version
with open("temscript/version.py") as fp:
    exec(fp.read())

# Only build _temscript c++ adapter on windows platforms
if sys.platform == 'win32':
    py_includes = [os.path.join(get_python_inc(), '../Lib/site-packages/numpy/core/include/')]
    ext_modules = [Extension('_temscript', glob.glob(os.path.join('_temscript_module', '*.cpp')), include_dirs=py_includes)]
else:
    ext_modules = []

setup(name='temscript',
      version=__version__,
      description='TEM Scripting adapter for FEI microscopes',
      author='Tore Niermann',
      author_email='tore.niermann@tu-berlin.de',
      packages=['temscript'],
      license="BSD 3-Clause License",
      ext_modules=ext_modules,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 2',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Software Development :: Libraries'
                   'License :: OSI Approved :: BSD License'],
      install_requires=['numpy', 'enum34;python_version<"3.4"'],
      entry_points={'console_scripts': ['temscript-server = temscript.server:run_server']},
      project_urls={"Source Code": "https://github.com/niermann/temscript"}
      )
