.. currentmodule:: temscript

.. _microscope:

The Microscope classes
======================

Several classes with a more pythonic interface exists. All these classes implement the same methods as described by
the :class:`BaseMicroscope`. Currently the following implementations exists:

* Local Microscope via the :class:`Microscope` class.
* Dummy Microscope via the :class:`NullMicroscope` class.
* Remove Microscope via the :class:`RemoteMicroscope` class.

The BaseMicroscope class
------------------------

.. autoclass:: BaseMicroscope
    :members:


The Microscope class itself
---------------------------

The :class:`Microscope` class provides a interface to the microscope if the script is run locally on the microscope's
computer. See :class:`BaseMicroscope` for a description of its methods.

.. autoclass:: Microscope

The RemoteMicroscope class
--------------------------

The :class:`RemoteMicroscope` provides the same methods as the :class:`Microscope` class, but connects to a remote
microscope server.

The temscript server must be running on the microscope PC. See section :ref:`server` for details.

.. autoclass:: RemoteMicroscope
    :members:


The NullMicroscope class
------------------------

The :class:`NullMicroscope` is a dummy replacement :class:`Microscope` class, which emulates the
microscope.

.. autoclass:: NullMicroscope
    :members:
