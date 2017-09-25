.. _pdc_client:

Script pdc_client
=================

.. note::

   Add argument ``-h`` or ``--help`` to get general help or help for a command.

This is a very simple client. Essentially this is just a little more
convenient than using ``curl`` manually. Each invocation of this client
obtains a token and then performs a single request.

This client is not meant for direct usage, but just as a helper for
integrating with PDC from languages where it might be easier than
performing the network requests manually.

