.. module:: temscript

A more python-like interface
============================

The Microscope class
^^^^^^^^^^^^^^^^^^^^

For a FEI microscope connected to the local computer, the :class:`Microscope` class provides an interface to this
microscope:

.. autoclass:: Microscope
    :members:

The RemoteMicroscope class
^^^^^^^^^^^^^^^^^^^^^^^^^^

The :class:`RemoteMicroscope` provides the same methods as the :class:`Microscope` class, but connects to a remote
microscope server.

The remote server is run by using the ``temscript-server`` command line script provided with the `temscript` package.

.. code-block:: none

    usage: test.py [-h] [-p PORT] [--host HOST]

    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  Specify port on which the server is listening
      --host HOST           Specify host address on which the the server is
                            listening

.. autoclass:: RemoteMicroscope
    :members:


The NullMicroscope class
^^^^^^^^^^^^^^^^^^^^^^^^^^

The :class:`NullMicroscope` provides the same methods as the :class:`Microscope` class, but only emulates the
microscope.

.. autoclass:: NullMicroscope
    :members:
