Welcome to temscript's documentation!
=====================================

Contents:

.. toctree::
    :maxdepth: 2
   
    microscope
    instrument
    restrictions
   
Introduction:
=============

Most objects of the :mod:`temscript` will behave as there COM counterpart, 
which are described more in detail in the scripting manual of your microscope
(usually in the file ``scripting.pdf`` located in the ``C:\Titan\Tem_help\manual`` or 
``C:\Tecnai\tem_help\manual`` directories).

The manual is your ultimate reference, this documentation will only describe the
python wrapper to the COM interface.

Enumerations
^^^^^^^^^^^^

Many of the attributes return values from enumerations. These enumerations can be found in the
:mod:`temscript.enums` module.

.. versionchanged:: 2.0
    All methods of the COM interface now directly return the enumeration objects. The constants
    from temscript version 1.x are not defined anymore. The numerical values still can be accessed
    by querying the corresponding enum, e.g. ``psmSA`` corresponds to ``ProjectionSubMode.SA``.

Vectors
^^^^^^^

Some object attributes handle with two dimensional vectors (e.g. ``ImageShift``). These 
attributes return ``(x, y)`` like tuples and expect iterable objects (``tuple``,
``list``, ...) with two floats when written (numpy arrays with two entries also work).
   
Globals
^^^^^^^

.. data:: version

    A string describing the version of temscript in the format 'X.Y.Z'.
    Current value is '|release|'. This is not the version of the TEMScripting interface
    (which can't be queried such easily).

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
