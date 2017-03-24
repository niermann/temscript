Welcome to temscript's documentation!
=====================================

Contents:

.. toctree::
    :maxdepth: 2
   
    microscope
    instrument
   
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

Many of the object's attributes actually return values from enumeration. The Python
wrappers of these attributes will return an integer value. There are constants in the
:mod:`temscript` module representing the enumeration values (e.g. ``pmImaging`` and ``pmDiffraction``
for the ``Mode`` attribute of the :class:`Projection` object). Since version 1.0.5 there are also
python enums for these, which can be found in the :mod:`temscript.enums` module and are imported
into the :mod:`temscript` namespace.

Vectors
^^^^^^^

Some object attributes handle with two dimensional vectors (e.g. ``ImageShift``). These 
attributes returns ``(x,y)`` like tuples on the Python side and expect sequence objects (``tuple``, 
``list``, ...) of floats of length two when written (numpy arrays with two entries also work).
   
Collections
^^^^^^^^^^^

Collections will be returned as list or tuple of objects. In future versions this might change,
and dictionaries will be returned.

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
