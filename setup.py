#!/usr/bin/env python3
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Long description
with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

# Read version
with open("temscript/version.py") as fp:
    exec(fp.read())

setup(name='temscript',
    version=__version__,
    description='TEM Scripting adapter for FEI microscopes',
    author='Tore Niermann',
    author_email='tore.niermann@tu-berlin.de',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['temscript'],
    platforms=['any'],
    license="BSD 3-Clause License",
    python_requires='>=3.4',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent'
    ],
    install_requires=['numpy'],
    entry_points={'console_scripts': ['temscript-server = temscript.server:run_server']},
    url="https://github.com/niermann/temscript",
    project_urls={
        "Source": "https://github.com/niermann/temscript",
        'Documentation': "https://temscript.readthedocs.io/"
    }
)
