.. _config:

Configuration
=============

The client can read server connection details from a configuration file.
The configuration file should be located in
``/etc/pdc.d/`` directory which contains ``fedora.json``, or in ``~/.config/pdc/client_config.json``.
If both files are present, the system one is loaded first and the user
configuration is applied on top of it (to add other options or overwrite
existing ones).

The configuration file should contain a JSON object, which maps server
name to JSON object with details. The name is an arbitrary string used
at client run time to identify which server you want to connect to.

The details of a single server must contain at least one key: ``host``
which specifies the URL to the API root (e.g.
``http:://localhost:8000/rest_api/v1/`` for local instance).

Other possible keys are:

* ``token``

    If specified, this token will be used for authentication. The client
    will not try to obtain any token from the server.

* ``ssl-verify``

    If set to ``false``, server certificate will not be validated. See [Python requests documentation](http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification) for other possible values.

* ``develop``

    When set to ``true``, the client will not use any authentication at
    all, not requesting a token nor sending any token with the requests.
    This is only useful for working with servers which don't require
    authentication.

* ``plugins``

    Plugins are configurable which depends on the user's needs.
    If no plugins are configured, the default plugins will be used.
    If plugins are configured, they will be merged to the default ones.

Example
-------

This config defines connection to development server running on
localhost and a production server:

.. code-block:: json

    {
        "local": {
            "host": "http://localhost:8000/rest_api/v1/",
            "develop": true,
            "ssl-verify": false
        },
        "prod": {
            "host": "https://pdc.example.com/rest_api/v1/",
            "plugins": ["permission.py", "release.py"]
        }
    }

