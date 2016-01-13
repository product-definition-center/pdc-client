# Client for Product Definition Center(PDC) in Python

[![Build Status](https://travis-ci.org/product-definition-center/pdc-client.svg?branch=master)](https://travis-ci.org/product-definition-center/pdc-client)
[![Coverage Status](https://coveralls.io/repos/product-definition-center/pdc-client/badge.svg?branch=master&service=github)](https://coveralls.io/github/product-definition-center/pdc-client?branch=master)

## Installation

You can obtain the client from the same repository where PDC server is.

## Configuration

The client can read server connection details from a configuration file.
The configuration file should be located in
`/etc/pdc/client_config.json` or in `~/.config/pdc/client_config.json`.
If both files are present, the system one is loaded first and the user
configuration is applied on top of it (to add other options or overwrite
existing ones).

The configuration file should contain a JSON object, which maps server
name to JSON object with details. The name is an arbitrary string used
at client run time to identify which server you want to connect to.

The details of a single server must contain at least one key: `host`
which specifies the URL to the API root (e.g.
`http:://localhost:8000/rest_api/v1/` for local instance).

Other possible keys are:

* `token`

    If specified, this token will be used for authentication. The client
    will not try to obtain any token from the server.

* `insecure`

    If set to `true`, server certificate will not be validated.

* `develop`

    When set to `true`, the client will not use any authentication at
    all, not requesting a token nor sending any token with the requests.
    This is only useful for working with servers which don't require
    authentication.

### Example system configuration

This config defines connection to development server running on
localhost and a production server. :

    {
        "local": {
            "host": "http://localhost:8000/rest_api/v1/",
            "develop": true,
            "insecure": false
        },
        "prod": {
            "host": "https://pdc.example.com/rest_api/v1/",
        }
    }

## Usage

The client package contains two separate clients. Both contain extensive
built-in help. Just run the executable with `-h` or `--help` argument.

### `pdc_client`

This is a very simple client. Essentially this is just a little more
convenient than using `curl` manually. Each invocation of this client
obtains a token and then performs a single request.

This client is not meant for direct usage, but just as a helper for
integrating with PDC from languages where it might be easier than
performing the network requests manually.

### `pdc`

This is much more user friendly user interface. A single invocation can
perform multiple requests depending on what subcommand you used.

The `pdc` client supports Bash completion if argcomplete Python package is installed.

If you installed client from rpm package, the completion file `pdc.bash` has been
installed to `/etc/bash_completion.d/`.

For developers or users who try to run `pdc` from source, to enable completion,
run this in your terminal (assuming pdc is somewhere on path).

    eval "$(register-python-argcomplete pdc)"

or put `pdc.bash` to `/etc/bash_completion.d/`.

## Python API

When writing a client code interfacing with PDC server, you might find
`PDCClient` handy. It provides access to the configuration defined above
and automates obtaining authorization token.

To use this module, you will need to install its dependencies. These
include

- [requests](http://docs.python-requests.org/en/latest/)
- [requests-kerberos](https://github.com/requests/requests-kerberos/)
- [beanbag](http://beanbag.readthedocs.org/en/latest/)
- (Optional)[argcomplete](http://argcomplete.readthedocs.org/en/latest/_modules/argcomplete.html)

Please find more details at： [`PDCClient`](pdc_client/__init__.py#L71)

When working with paginated responses, there is a function([`get_paged`](pdc_client/__init__.py#L138)) to
simplify that. From client code it is iterating single object. Behind
the scenes it will download the first page, once all results from that
page are exhausted, it will get another page until everything is
processed.

### Examples

- [Creating global components based on imported source RPMs](https://github.com/product-definition-center/product-definition-center/blob/master/pdc/scripts/create_release_components.py)
- [Find components with multiple contacts of same role](https://gist.github.com/lubomir/c78091bf286ee9764f99)

## Known Issues

### Kerberos

Under enterprise network, [Reverse DNS
mismatches](http://web.mit.edu/Kerberos/www/krb5-latest/doc/admin/princ_dns.html#reverse-dns-mismatches)
may cause problems authenticating with Kerberos.

If you can successfully run `kinit` but not authenticate yourself to PDC
servers, check `/etc/krb5.conf` and make sure that `rdns` is set to
false in `libdefaults` section. :

    [libdefaults]
        rdns = false

## For Developers

### Installation details

1.  yum repository

    Enable PDC yum repository, install PDC Client by :

        $ sudo yum install pdc-client -y

2.  build from source

    If you have got the code and setup your development environment,
    then you could build from source and install the client :

        $ git checkout `{release-tag}`
        $ cd product-definition-center/pdc_client
        $ tito build --rpm --offline
        $ sudo yum install /tmp/tito/noarch/pdc-client*.noarch.rpm

### General

The PDC Client (package name: pdc\_client) is mainly build up with
Python argparse module and PDC's Python module pdc\_client.

It is powered by [`BeanBag`](http://beanbag.readthedocs.org/en/latest/), a simple module that lets you access REST
APIs in an easy way.
