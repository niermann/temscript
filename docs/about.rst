.. currentmodule:: temscript

About
=====

Introduction
------------

The ``temscript`` package provides a Python wrapper for the scripting
interface of Thermo Fisher Scientific and FEI microscopes. The functionality is
limited to the functionality of the original scripting interface. For detailed information
about TEM scripting see the documentation accompanying your microscope.

The ``temscript`` package provides two interfaces to the microsope. The first one
corresponds directly to the COM interface and is implemented by the :class:`Instrument` class. A more thorough
description of this interface can be found in the :ref:`instrument` section.

The other interface is provided by the :class:`Microscope` class. While instances of the :class:`temscript.Microscope` class
operate on the computer connected to the microscope directly, there are two replacement classes, which provide the
same interface to as the :class:`Microscope` class. The first one, :class:`RemoteMicroscope` allows to operate the
microscope remotely from a computer, which is connected to the microscope PC via network. The other one,
:class:`NullMicroscope` serves as dummy replacement for offline development. A more thorough
description of this interface can be found in the :ref:`microscope` section.

For remote operation of the microscope the temscript server must run on the microscope PC. See section :ref:`server`
for details.

The section :ref:`restrictions` describes some known issues with the scripting interface itself. These are restrictions
of the original scripting interface and not issues related to the ``temscript`` package itself.

Quick example
-------------

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
