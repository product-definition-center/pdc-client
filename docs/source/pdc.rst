.. _pdc:

Script pdc
==========

.. note::

   Use argument ``-h`` or ``--help`` to get general help or help for a command.

This has much more user friendly user interface than ``pdc_client``. A single
invocation can perform multiple requests depending on what subcommand you used.

The ``pdc`` client supports Bash completion if argcomplete Python package is installed.

If you installed client from rpm package, the completion file ``pdc.bash`` has been
installed to ``/etc/bash_completion.d/``.

For developers or users who try to run ``pdc`` from source, to enable completion,
run this in your terminal (assuming pdc is somewhere on path).

.. code-block:: bash

   eval "$(register-python-argcomplete pdc)"

or put ``pdc.bash`` to ``/etc/bash_completion.d/``.

