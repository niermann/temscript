Welcome to temscript's documentation!
=====================================

Contents:

.. toctree::
    :maxdepth: 2
   
    instrument
    microscope
    server
    restrictions
    changelog
   
Introduction:
=============

The ``temscript`` package provides a Python wrapper for the scripting
interface of Thermo Fisher Scientific and FEI microscopes. The functionality is
limited to the functionality of the original scripting interface. For detailed information
about TEM scripting see the documentation accompanying your microscope.

The ``temscript`` package provides two interfaces to the microsope. The first one
corresponds directly to the COM interface and is implemented by the :class:`temscript.Instrument` class. A more thorough
description of this interface can be found in the :ref:`instrument` section.

The other interface is provided by the :class:`temscript.Microscope` class. While instances of the :class:`temscript.Microscope` class
operate on the computer connected to the microscope directly, there are two replacement classes, which provide the
same interface to as the :class:`temscript.Microscope` class. The first one, :class:`temscript.RemoteMicroscope` allows to operate the
microscope remotely from a computer, which is connected to the microscope PC via network. The other one,
:class:`temscript.NullMicroscope` serves as dummy replacement for offline development. A more thorough
description of this interface can be found in the :ref:`microscope` section.

For remote operation of the microscope the temscript server must run on the microscope PC. See section :ref:`server`
for details.

The section :ref:`restrictions` describes some known issues with the scripting interface itself. These are restrictions
of the original scripting interface and not issues related to the ``temscript`` package itself.

Quick example
=============

Execute this on the microscope PC (with ``temscript`` package installed) to create an instance of the local
:class:`Microscope` interface:

    >>> import temscript
    >>> microscope = temscript.Microscope()

Show the current acceleration voltage:

    >>> microscope.get_voltage()
    300.0

Move beam:

    >>> beam_pos = microscope.get_beam_shift()
    >>> print(beam_pos)
    (0.0, 0.0)
    >>> new_beam_pos = beam_pos[0], beam_pos[1] + 1e-6
    >>> microscope.set_beam_shift(new_beam_pos)

Globals
=======

.. data:: version

    A string describing the version of temscript in the format 'X.Y.Z'.
    Current value is '|release|'. This is not the version of the TEMScripting interface
    (which can't be queried such easily).

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


Copyright & Disclaimer
======================

Copyright (c) 2012-2021 by Tore Niermann
Contact: tore.niermann (at) tu-berlin.de

All product and company names are trademarks or registered trademarks
of their respective holders. Use of them does not imply any affiliation
with or endorsement by them.

temscript is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
LICENCE.txt file for any details.

All product and company names are trademarks or registered trademarks of
their respective holders. Use of them does not imply any affiliation
with or endorsement by them.
