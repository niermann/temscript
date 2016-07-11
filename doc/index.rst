Welcome to temscript's documentation!
=====================================

Contents:

.. toctree::
   :maxdepth: 2
   
   module
   
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
for the ``Mode`` attribute of the :class:`Projection` object)

Vectors
^^^^^^^

Some object attributes handle with two dimensional vectors (e.g. ``ImageShift``). These 
attributes returns ``(x,y)`` like tuples on the Python side and expect sequence objects (``tuple``, 
``list``, ...) of floats of length two when written (numpy arrays with two entries also work).
   
Collections
^^^^^^^^^^^

Collections will be returned as list or tuple of objects. In future versions this might change,
and dictionaries will be returned.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
